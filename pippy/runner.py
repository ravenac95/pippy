import sys
from pip import version_control
from pip.commands.install import InstallCommand
from pip.index import PackageFinder
from pip.baseparser import parser

class ExactPackageFinder(PackageFinder):
    def find_requirement(self, req, upgrade):
        absolute_versions = map(lambda a: a, req.absolute_versions)
        if absolute_versions:
            if len(absolute_versions) > 1:
                # if there is more than one absolute version it doesn't
                # make any sense whatsoever
                raise AttributeError('Contradictory version specs')
            absolute_version = absolute_versions[0]
            local_link = self._find_locally(req.name, absolute_version)
            if local_link:
                # Check locally for the absolute version
                # if is available
                found_link = local_link
            else:
                # otherwise use the original find_requirements
                # it'll automatically get cached and saved when downloaded 
                # later
                found_link = super(ExactPackageFinder, self).find_requirement(
                    req, upgrade)
        else:
            found_link = super(ExactPackageFinder, self).find_requirement(
                    req, upgrade)
            link_tuple = self._link_package_versions(found_link, req.name.lower())
            found_version = link_tuple[0][2]
            local_link = self._find_locally(req.name, found_version)
            # Check if this version we found is already available 
            # locally
            if local_link:
                found_link = local_link
        return found_link

    def _find_locally(self, name, version):
        # FIXME not implemented
        return False

class ExactInstallCommand(InstallCommand):
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
