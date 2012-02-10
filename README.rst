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
                    .. tons of zips ..
                package-name/
                package-name/
            2.5/    # <- stores builds for python 2.5
                package-name/
                    .. tons of zips ..
            2.6/    # <- for python 2.6
            ... more python versions ...
            
