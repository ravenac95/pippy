import sys
import os
import shutil
import re
import zipfile
import pkg_resources
import tempfile
from functools import wraps
from pip.locations import bin_py, running_under_virtualenv
from pip.exceptions import (InstallationError, UninstallationError,
                            BestVersionAlreadyInstalled)
from pip.vcs import vcs
from pip.log import logger
from pip.util import display_path, rmtree
from pip.util import ask, ask_path_exists, backup_dir
from pip.util import is_installable_dir, is_local, dist_is_local
from pip.util import renames, normalize_path, egg_link_path
from pip.util import make_path_relative
from pip import call_subprocess
from pip.backwardcompat import (any, copytree, urlparse, urllib,
                                ConfigParser, string_types, HTTPError,
                                FeedParser, get_python_version,
                                b)
from pip.index import Link
from pip.locations import build_prefix
from pip.download import (get_file_content, is_url, url_to_path,
                          path_to_url, is_archive_file,
                          unpack_vcs_link, is_vcs_url, is_file_url,
                          unpack_file_url, unpack_http_url)
from pip import req
from pip.req import *
from utils import *
from finder import *
from config import pippy_home

PIP_DELETE_MARKER_FILENAME = 'pip-delete-this-directory.txt'

def run_build(req, req_version, link, location):
    build_cache_path = build_path(pippy_home(), req.name, req_version)
    if not os.path.exists(build_cache_path):
        try:
            os.makedirs(os.path.dirname(build_cache_path))
        except OSError:
            pass
        logger.notify('Attempting to cache build of package "%s"' % req.name)
        try:
            call_subprocess(
                [sys.executable, 'setup.py', 'build'],
                cwd=location, show_stdout=False,
                command_level=logger.VERBOSE_DEBUG,
                command_desc='python setup.py build')
        except:
            # for now just reraise
            logger.notify('Build of package "%s" failed' % req.name)
            raise
        logger.notify('Build succeeded for "%s"' % req.name)
        tar_gzip_dir(location, build_cache_path, base=req.name)

def cache_download(req, req_version, link, location):
    # Does the current requirement exist in the 
    # Build the directory
    source_cache_path = source_path(pippy_home(), req.name, req_version)
    if not os.path.exists(source_cache_path):
        # if the path does not exist. tar gzip the folder and cache it
        try:
            os.makedirs(os.path.dirname(source_cache_path))
        except OSError:
            # Do nothing the directory is already made
            pass
        logger.notify('Caching "%s" locally' % req.name)
        tar_gzip_dir(location, source_cache_path, base=req.name)
    run_build(req, req_version, link, location)

def wrap_unpack(f):
    @wraps(f)
    def unpack_wrapper(req, req_version, link, location, *args, **kwargs):
        # Download the file
        wrapped_return = f(link, location, *args, **kwargs)
        # Save the download
        cache_download(req, req_version, link, location)
        return wrapped_return
    return unpack_wrapper

unpack_file_url = wrap_unpack(req.unpack_file_url)
unpack_http_url = wrap_unpack(req.unpack_http_url)
req.unpack_file_url = unpack_file_url
req.unpack_http_url = unpack_http_url


class PippyRequirementSet(req.RequirementSet):
    def __init__(self, *args, **kwargs):
        super(PippyRequirementSet, self).__init__(*args, **kwargs)

    # Almost entirely copied from original pip source
    def prepare_files(self, finder, force_root_egg_info=False, bundle=False):
        """Prepare process. Create temp directories, download and/or unpack files."""
        unnamed = list(self.unnamed_requirements)
        reqs = list(self.requirements.values())
        while reqs or unnamed:
            if unnamed:
                req_to_install = unnamed.pop(0)
            else:
                req_to_install = reqs.pop(0)
            req_version = None
            install = True
            best_installed = False
            if not self.ignore_installed and not req_to_install.editable:
                req_to_install.check_if_exists()
                if req_to_install.satisfied_by:
                    if self.upgrade:
                        if not self.force_reinstall:
                            try:
                                url, req_version = finder.find_requirement(
                                    req_to_install, self.upgrade)
                            except BestVersionAlreadyInstalled:
                                best_installed = True
                                install = False
                            else:
                                # Avoid the need to call find_requirement again
                                req_to_install.url = url.url

                        if not best_installed:
                            req_to_install.conflicts_with = req_to_install.satisfied_by
                            req_to_install.satisfied_by = None
                    else:
                        install = False
                if req_to_install.satisfied_by:
                    if best_installed:
                        logger.notify('Requirement already up-to-date: %s'
                                      % req_to_install)
                    else:
                        logger.notify('Requirement already satisfied '
                                      '(use --upgrade to upgrade): %s'
                                      % req_to_install)
            if req_to_install.editable:
                logger.notify('Obtaining %s' % req_to_install)
            elif install:
                if req_to_install.url and req_to_install.url.lower().startswith('file:'):
                    logger.notify('Unpacking %s' % display_path(url_to_path(req_to_install.url)))
                else:
                    logger.notify('Downloading/unpacking %s' % req_to_install)
            logger.indent += 2
            try:
                is_bundle = False
                if req_to_install.editable:
                    if req_to_install.source_dir is None:
                        location = req_to_install.build_location(self.src_dir)
                        req_to_install.source_dir = location
                    else:
                        location = req_to_install.source_dir
                    if not os.path.exists(self.build_dir):
                        _make_build_dir(self.build_dir)
                    req_to_install.update_editable(not self.is_download)
                    if self.is_download:
                        req_to_install.run_egg_info()
                        req_to_install.archive(self.download_dir)
                    else:
                        req_to_install.run_egg_info()
                elif install:
                    ##@@ if filesystem packages are not marked
                    ##editable in a req, a non deterministic error
                    ##occurs when the script attempts to unpack the
                    ##build directory

                    location = req_to_install.build_location(self.build_dir, not self.is_download)
                    ## FIXME: is the existance of the checkout good enough to use it?  I don't think so.
                    unpack = True
                    if not os.path.exists(os.path.join(location, 'setup.py')):
                        ## FIXME: this won't upgrade when there's an existing package unpacked in `location`
                        if req_to_install.url is None:
                            url, req_version = finder.find_requirement(req_to_install, upgrade=self.upgrade)
                        else:
                            ## FIXME: should req_to_install.url already be a link?
                            url = Link(req_to_install.url)
                            assert url
                        if url:
                            try:
                                self.unpack_url(req_to_install, req_version, url, location, self.is_download)
                            except HTTPError:
                                e = sys.exc_info()[1]
                                logger.fatal('Could not install requirement %s because of error %s'
                                             % (req_to_install, e))
                                raise InstallationError(
                                    'Could not install requirement %s because of HTTP error %s for URL %s'
                                    % (req_to_install, e, url))
                        else:
                            unpack = False
                    if unpack:
                        is_bundle = req_to_install.is_bundle
                        url = None
                        if is_bundle:
                            req_to_install.move_bundle_files(self.build_dir, self.src_dir)
                            for subreq in req_to_install.bundle_requirements():
                                reqs.append(subreq)
                                self.add_requirement(subreq)
                        elif self.is_download:
                            req_to_install.source_dir = location
                            if url and url.scheme in vcs.all_schemes:
                                req_to_install.run_egg_info()
                                req_to_install.archive(self.download_dir)
                        else:
                            req_to_install.source_dir = location
                            req_to_install.run_egg_info()
                            if force_root_egg_info:
                                # We need to run this to make sure that the .egg-info/
                                # directory is created for packing in the bundle
                                req_to_install.run_egg_info(force_root_egg_info=True)
                            req_to_install.assert_source_matches_version()
                            #@@ sketchy way of identifying packages not grabbed from an index
                            if bundle and req_to_install.url:
                                self.copy_to_build_dir(req_to_install)
                                install = False
                        # req_to_install.req is only avail after unpack for URL pkgs
                        # repeat check_if_exists to uninstall-on-upgrade (#14)
                        req_to_install.check_if_exists()
                        if req_to_install.satisfied_by:
                            if self.upgrade or self.ignore_installed:
                                req_to_install.conflicts_with = req_to_install.satisfied_by
                                req_to_install.satisfied_by = None
                            else:
                                install = False
                if not is_bundle and not self.is_download:
                    ## FIXME: shouldn't be globally added:
                    finder.add_dependency_links(req_to_install.dependency_links)
                    if (req_to_install.extras):
                        logger.notify("Installing extra requirements: %r" % ','.join(req_to_install.extras))
                    if not self.ignore_dependencies:
                        for req in req_to_install.requirements(req_to_install.extras):
                            try:
                                name = pkg_resources.Requirement.parse(req).project_name
                            except ValueError:
                                e = sys.exc_info()[1]
                                ## FIXME: proper warning
                                logger.error('Invalid requirement: %r (%s) in requirement %s' % (req, e, req_to_install))
                                continue
                            if self.has_requirement(name):
                                ## FIXME: check for conflict
                                continue
                            subreq = InstallRequirement(req, req_to_install)
                            reqs.append(subreq)
                            self.add_requirement(subreq)
                    if req_to_install.name not in self.requirements:
                        self.requirements[req_to_install.name] = req_to_install
                else:
                    self.reqs_to_cleanup.append(req_to_install)
                if install:
                    self.successfully_downloaded.append(req_to_install)
                    if bundle and (req_to_install.url and req_to_install.url.startswith('file:///')):
                        self.copy_to_build_dir(req_to_install)
            finally:
                logger.indent -= 2
    
    def unpack_url(self, req, req_version, link, location, only_download=False):
        if only_download:
            location = self.download_dir
        if is_vcs_url(link):
            return unpack_vcs_link(link, location, only_download)
        elif is_file_url(link):
            return unpack_file_url(req, req_version, link, location)
        else:
            if self.download_cache:
                self.download_cache = os.path.expanduser(self.download_cache)
            return unpack_http_url(req, req_version, link, location, 
                    self.download_cache, only_download)
