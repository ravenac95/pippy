from setuptools import setup, find_packages
import sys, os

VERSION = '0.1.0'

LONG_DESCRIPTION = open('README.rst').read()

setup(name='pippy',
    version=VERSION,
    description="pippy - Faster installs!",
    long_description=LONG_DESCRIPTION,
    keywords='',
    author='Reuven V. Gonzales',
    author_email='reuven@tobetter.us',
    url="https://github.com/ravenac95/pippy",
    license='MIT',
    platforms='*nix',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pip',
    ],
    entry_points={
        'console_scripts': [
            'pippy = pippy.runner:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Build Tools',
    ],
)
