import os
import sys
import platform
import tarfile

def get_implementation():
    return platform.python_implementation()

def get_python_version_str():
    version_info = map(str, sys.version_info[:2])
    version = ''.join(version_info)
    return "py%s" % version

def tar_gzip_dir(directory, destination, base=None):
    """Creates a tar.gz from a directory."""
    dest_file = tarfile.open(destination, 'w:gz')
    abs_dir_path = os.path.abspath(directory)
    base_name = abs_dir_path + "/"
    base = base or os.path.basename(directory)
    for path, dirnames, filenames in os.walk(abs_dir_path):
        rel_path = path[len(base_name):]
        dir_norm_path = os.path.join(base, rel_path)
        dir_tar_info = dest_file.gettarinfo(name=path)
        dir_tar_info.name = dir_norm_path
        dest_file.addfile(dir_tar_info)
        for filename in filenames:
            actual_path = os.path.join(path, filename)
            norm_path = os.path.join(base, rel_path, filename)
            tar_info = dest_file.gettarinfo(name=actual_path)
            tar_info.name = norm_path
            new_file = open(actual_path, 'rb')
            dest_file.addfile(tar_info, new_file)
    dest_file.close()
