import cgi
import getpass
import mimetypes
import os
import re
import shutil
import sys
import tempfile
from pip.backwardcompat import (md5, copytree, xmlrpclib, urllib, urllib2,
                                urlparse, string_types, HTTPError)
from pip.exceptions import InstallationError
from pip.util import (splitext, rmtree,
                      format_size, display_path, backup_dir, ask,
                      unpack_file, create_download_cache_folder, cache_download)
from pip.vcs import vcs
from pip.log import logger

def unpack_http_url(link, location, download_cache, only_download):
    temp_dir = tempfile.mkdtemp('-unpack', 'pip-')
    target_url = link.url.split('#', 1)[0]
    target_file = None
    download_hash = None
    if download_cache:
        target_file = os.path.join(download_cache,
                                   urllib.quote(target_url, ''))
        if not os.path.isdir(download_cache):
            create_download_cache_folder(download_cache)
    if (target_file
        and os.path.exists(target_file)
        and os.path.exists(target_file + '.content-type')):
        fp = open(target_file+'.content-type')
        content_type = fp.read().strip()
        fp.close()
        if link.md5_hash:
            download_hash = _get_md5_from_file(target_file, link)
        temp_location = target_file
        logger.notify('Using download cache from %s' % target_file)
    else:
        resp = _get_response_from_url(target_url, link)
        content_type = resp.info()['content-type']
        filename = link.filename  # fallback
        # Have a look at the Content-Disposition header for a better guess
        content_disposition = resp.info().get('content-disposition')
        if content_disposition:
            type, params = cgi.parse_header(content_disposition)
            # We use ``or`` here because we don't want to use an "empty" value
            # from the filename param.
            filename = params.get('filename') or filename
        ext = splitext(filename)[1]
        if not ext:
            ext = mimetypes.guess_extension(content_type)
            if ext:
                filename += ext
        if not ext and link.url != geturl(resp):
            ext = os.path.splitext(geturl(resp))[1]
            if ext:
                filename += ext
        temp_location = os.path.join(temp_dir, filename)
        download_hash = _download_url(resp, link, temp_location)
    if link.md5_hash:
        _check_md5(download_hash, link)
    if only_download:
        _copy_file(temp_location, location, content_type, link)
    else:
        unpack_file(temp_location, location, content_type, link)
    if target_file and target_file != temp_location:
        cache_download(target_file, temp_location, content_type)
    if target_file is None:
        os.unlink(temp_location)
    os.rmdir(temp_dir)
