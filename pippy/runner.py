import sys
import argparse
from pip import version_control
from pip import req
from pip.commands import install
from pip.baseparser import parser as pip_parser
from finder import *
from req import PippyRequirementSet

# Monkey patch the RequirementSet
install.RequirementSet = PippyRequirementSet


class ExactInstallCommand(install.InstallCommand):
    def _build_package_finder(self, options, index_urls):
        return ExactPackageFinder(find_links=options.find_links,
                             index_urls=index_urls,
                             use_mirrors=options.use_mirrors,
                             mirrors=options.mirrors)

main_parser = argparse.ArgumentParser(
    description='Install pip requirements using a local cache')
main_parser.add_argument('file', help='a pip requirements file')

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    version_control()
    install = ExactInstallCommand()
    options, pargs = pip_parser.parse_args([])
    cli_options = main_parser.parse_args(args)
    requirements_file = cli_options.file
    install.main(['-r', requirements_file], options)

if __name__ == '__main__':
    main()
