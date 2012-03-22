pippy
=====

pippy is a pip extension that will allow you to keep local copies of prebuilt
python packages. It's main purpose is to be used with virtstrap so that
virtstrap can create copies of each project without ever having to download or
build anything.

The folder structure that I'm currently thinking of using is this::

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

The CLI currently provides a single command, the ``install`` command::
    
    pippy install [requirementsfile]

This command accepts a pip requirements file. It is highly suggested that the
requirements file use only exact specifications for the requirements

Future Commands
---------------

- ``manage`` - Will manage all the packages in pippy's cache.
- ``uninstall`` - A convenience operation to pip's uninstall command

Configuration
-------------

By default pippy will use ``~/.pippy`` as the directory for it's cache.
However, you can set this value by changing the ``PIPPY_CACHE`` environment
variable to point to the correct directory. You must have write permissions to
that directory or else pippy will not work.
