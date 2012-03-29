pippy
=====

pippy is a pip extension that will allow you to keep local copies of prebuilt
python packages. It's main purpose is to be used with virtstrap so that
virtstrap can create copies of each project without ever having to download or
build anything. It accomplishes this only when it knows the exact version of
the package you wish to download. Otherwise it behaves just as pip would
behave.

Since virtstrap generates a VEfile.lock (similar to Ruby Bundler's
Gemfile.lock). Virtstrap tracks the exact version of the software you're using.
For this very reason, pippy is planned to be included in virtstrap.

Local Package Storage
---------------------

By default pippy stores all of the packages in ``~/.pippy``. To change this
directory just change the environment variable ``PIPPY_CACHE`` to point to the
desired directory. The folder structure for the storage is this::

    ~/.pippy
        packages/
            source/ # <- stores the sources for packages
                package-name/
                    .. tons of zips/tars ..
                package-name/
                package-name/
            cpython/ # <- stores builds for cpython
                2.5/    # <- stores builds for python 2.5
                    package-name/
                        .. tons of tars ..
                2.6/    # <- for python 2.6
                ... more python versions ...
            pypy/ # <- stores builds for pypy
            ... more implementations ...

The CLI currently only accepts one argument, a pip requirements file::
    
    pippy [requirementsfile]

It is highly suggested that the requirements file use only exact specifications
for the requirements.

Further Development
-------------------

Eventually, pippy will provide almost the same commands as pip, plus some
additional commands for managing the installed packages.

Future Commands
^^^^^^^^^^^^^^^
- ``install`` - Will work the same as ``pip install``
- ``manage`` - Will manage all the packages in pippy's cache.
- ``uninstall`` - A convenience operation to pip's uninstall command

Known Issues
------------

These issues will be rectified as soon as possible

- Doesn't adequately support custom package indexes. It'll work, but it's use
  is highly discouraged at this time.
- Isn't known to work with Windows
