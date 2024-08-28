import re
from setuptools import Distribution
from .. import build_version

_P = re.compile(r"([-.]?[a-z]+)", re.I)


def configure(dist: Distribution):
    slf = __name__.split(".")[0]
    if slf in dist.setup_requires:
        if v := dist.metadata.version:
            v = _P.split(v, 1)[0]
        dist.metadata.version = build_version(v)
