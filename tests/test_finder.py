from pippy.finder import *

def test_is_link_in_cache():
    tests = [
        'file://base/location',
        'file://base/src/somelocation',
    ]
    for test_link in tests:
        yield run_is_link_in_cache, '/base', test_link

def run_is_link_in_cache(base, link):
    assert is_link_in_cache(base, link)

def test_is_link_in_source_cache():
    tests = [
        'file://base/src/location',
        'file://base/src/somelocation',
    ]
    for test_link in tests:
        yield run_is_link_in_source_cache, '/base', test_link

def run_is_link_in_source_cache(base, link):
    assert is_link_in_source_cache(base, link)

def test_is_link_in_build_cache():
    tests = [
        ('file://base/cpython/py27', 'cpython', 'py27'),
        ('file://base/pypy/py27', 'pypy', 'py27'),
        ('file://base/pypy/py27', 'pypy', 'py27'),
    ]
    for test_link, implementation, version in tests:
        yield (run_is_link_in_build_cache, '/base', 
                test_link, implementation, version)

def run_is_link_in_build_cache(base, link, implementation, version):
    assert is_link_in_build_cache(base, link, py_implementation=implementation,
            py_version=version)

def test_source_path():
    path = source_path('/base', 'test', '0.1')
    assert path == '/base/src/test/test-0.1.tar.gz'

def test_build_path():
    path = build_path('/base', 'test', '0.1', py_implementation="pypy", 
            py_version="py27")
    assert path == '/base/pypy/py27/test/test-0.1.tar.gz'

def test_known_index_url_dir_works():
    tests = [
        # We just need the domain all else SHOULDN'T matter
        ('http://pypi.python.org/simple/', 'pypi.python.org'),
        ('http://pypi.python.org/asdfafefjasdfkjalsdfk/', 'pypi.python.org'),
        # Mirrors should resolve to the same directory
        ('http://a.pypi.python.org/', 'pypi.python.org'),
        ('http://b.pypi.python.org/', 'pypi.python.org'),
        ('http://c.pypi.python.org/', 'pypi.python.org'),
        ('http://d.pypi.python.org/', 'pypi.python.org'),
        ('http://e.pypi.python.org/', 'pypi.python.org'),
        ('http://f.pypi.python.org/', 'pypi.python.org'),
        ('http://g.pypi.python.org/', 'pypi.python.org'),
    ]
    for test_link, expected in tests:
        yield run_known_index_url_dir, test_link, expected

def run_known_index_url_dir(test_link, expected):
    index_dir = known_index_url_dir(test_link)
    assert index_dir == expected
