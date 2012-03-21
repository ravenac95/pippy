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
