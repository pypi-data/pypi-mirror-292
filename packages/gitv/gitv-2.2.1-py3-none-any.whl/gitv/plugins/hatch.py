from hatchling.plugin import hookimpl
from hatchling.version.source.plugin.interface import VersionSourceInterface
from .. import build_version


class GitVersionSource(VersionSourceInterface):
    PLUGIN_NAME = "vcs"

    def get_version_data(self) -> dict:
        return dict(version=build_version(self.config.get("version")))


@hookimpl
def hatch_register_version_source():
    return GitVersionSource
