import os
from pip.download import url_to_path
from pip.index import PackageFinder, Link
from pip.log import logger
from utils import get_implementation, get_python_version_str
from config import pippy_home

SOURCE_PATH = 'src'
EXTENSION = '.tar.gz'

class ExactPackageFinder(PackageFinder):
    def find_requirement(self, req, upgrade):
        absolute_versions = map(lambda a: a, req.absolute_versions)
        if absolute_versions:
            if len(absolute_versions) > 1:
                # if there is more than one absolute version it doesn't
                # make any sense whatsoever
                raise AttributeError('Contradictory version specs')
            found_version = absolute_versions[0]
            local_link = self._find_locally(req.name, found_version)
            if local_link:
                # Check locally for the absolute version
                # if is available
                found_link = local_link
            else:
                # otherwise use the original find_requirements
                # it'll automatically get cached and saved when downloaded 
                # later
                found_link = super(ExactPackageFinder, self).find_requirement(
                    req, upgrade)
        else:
            found_link = super(ExactPackageFinder, self).find_requirement(
                    req, upgrade)
            link_tuple = self._link_package_versions(found_link, req.name.lower())
            found_version = link_tuple[0][2]
            local_link = self._find_locally(req.name, found_version)
            # Check if this version we found is already available 
            # locally
            if local_link:
                found_link = local_link
        return found_link, found_version

    def _find_locally(self, name, version):
        # FIXME not implemented
        name = name.lower()
        local_path = build_cache(self.cache_path(), name, version)
        if not local_path:
            local_path = source_cache(self.cache_path(), name, version)
        else:
            logger.notify('Found locally at %s', local_path)
        if local_path:
            return Link("file:/%s" % local_path)
        return None

    def cache_path(self):
        return pippy_home()

def make_filename(name, version):
    filename = '%s-%s%s' % (name, version, EXTENSION)
    return filename

def source_path(cache_path, name, version):
    filename = make_filename(name, version)
    return os.path.abspath(os.path.join(cache_path, SOURCE_PATH, 
        name, filename))

def source_cache(cache_path, name, version):
    file_path = source_path(cache_path, name, version)
    if os.path.exists(file_path):
        return file_path
    return None

def build_path(cache_path, name, version, py_implementation=None,
        py_version=None):
    filename = make_filename(name, version)
    py_implementation = py_implementation or get_implementation()
    py_version = py_version or get_python_version_str()
    return os.path.abspath(os.path.join(cache_path, py_implementation, 
            py_version, name, filename))

def build_cache(cache_path, name, version, py_implementation=None,
        py_version=None):
    file_path = build_path(cache_path, name, version,
            py_implementation=py_implementation, py_version=py_version)
    if os.path.exists(file_path):
        return file_path
    return None

def is_link_in_cache(cache_path, link):
    try:
        path = url_to_path(link)
    except AssertionError:
        return False
    cache_path = os.path.abspath(cache_path)
    # If the path startswith cache_path
    # it is in the cache
    if path.startswith(cache_path):
        return True
    return False

def is_link_in_source_cache(cache_path, link):
    try:
        path = url_to_path(link)
    except AssertionError:
        return False
    source_path = os.path.abspath(os.path.join(cache_path, SOURCE_PATH))
    if path.startswith(source_path):
        return True
    return False

def is_link_in_build_cache(cache_path, link, 
        py_implementation=None, py_version=None):
    try:
        path = url_to_path(link)
    except AssertionError:
        return False
    py_implementation = py_implementation or get_implementation()
    py_version = py_version or get_python_version_str()
    build_path = os.path.abspath(os.path.join(
        cache_path, py_implementation, py_version))
    if path.startswith(build_path):
        return True
    return False
