import sys
from pip import version_control
from pip import req
from pip.commands import install
from pip.baseparser import parser
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

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    version_control()
    install = ExactInstallCommand()
    options, blargs = parser.parse_args([])
    install.main(['-r', 'requirements.txt'], options)

if __name__ == '__main__':
    main()
