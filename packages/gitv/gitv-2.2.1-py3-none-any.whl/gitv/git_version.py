from os import getenv
from re import fullmatch
from subprocess import CalledProcessError, check_output


def _git(cmd):
    try:
        stdout = check_output(cmd, shell=True, universal_newlines=True)
    except CalledProcessError:
        stdout = ""  # allow non git repo to build
    lines = [line.rstrip() for line in stdout.splitlines()]
    return [line for line in lines if line]


def _git_sha(name="HEAD"):
    sha = _git(f"git rev-list -n 1 {name}")
    return sha[0][:7] if sha else None


def _git_tag(name="HEAD"):
    tags = _git(f"git tag --points-at {name}")
    match = fullmatch("v(.*)", tags[0] if tags else "")
    return match.group(1) if match else None


def _git_branch(name="HEAD"):
    branches = _git("git branch --show-current")
    return branches[0] if branches else None


def build_version(version, sticky=False):
    version = version or "0.0.0"

    if tag := getenv("VERSIONING_GIT_TAG") or _git_tag():
        return version if sticky else tag

    build = getenv("BUILD_NUMBER", "")
    gitsha = _git_sha() or "local"
    branch = getenv("VERSIONING_GIT_BRANCH") or _git_branch()
    stage = "rc" if branch in ["main", "master"] else "dev"

    return f"{version}-{stage}{build}+{gitsha}"
