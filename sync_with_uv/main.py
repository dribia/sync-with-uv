"""Main module to synchronize .pre-commit-config.yaml with uv.lock."""

import argparse
import json
import re
from collections.abc import Sequence
from pathlib import Path
from string import Template

import yaml
from tomlkit.items import AoT
from tomlkit.toml_file import TOMLFile

from sync_with_uv.db import DEPENDENCY_MAPPING

YAML_FILE = ".pre-commit-config.yaml"
REV_LINE_RE = re.compile(
    r'^(\s+)rev:(\s*)(?P<quotes>[\'"]?)(?P<rev>[^\s#]+)(?P=quotes)(\s*)(# frozen: (?P<comment>\S+)\b)?(?P<rest>.*?)(?P<eol>\r?\n)$'  # noqa: E501
)
FROZEN_REV_RE = re.compile(r"[a-f\d]{40}")
ADD_DEP_RE = re.compile(
    r'^(\s+)-(\s*)(?P<quotes>[\'"]?)(?P<package>[A-Za-z0-9-_]+)(?P<limit>[><=]\S+)(?P=quotes)(\s*)(?P<rest>.*?)(?P<eol>\r?\n)$'
)


class UVItems:
    """A class to get and filter uv.lock packages to sync in .pre-commit-config.yaml."""

    def __init__(
        self,
        uv_list: AoT,
        skip: list[str] | None = None,
        db: dict[str, dict[str, str]] = DEPENDENCY_MAPPING,
    ) -> None:
        """Create a UVItems collection.

        Args:
            uv_list: a list of packages coming from uv.lock.
            skip: A list of packages to skip. Such packages won't
                be synchronized in .pre-commit-config.yaml.
            db: A package-repo mapping.
        """
        if skip is None:
            skip = []

        self._uv_lock = {}
        self.version = {}
        for package in uv_list:
            self.version[package["name"].lower().replace("_", "-")] = package["version"]
            if package["name"] in skip:
                continue

            dependency_mapping = db.get(package["name"], None)
            if dependency_mapping:
                name = package["name"]
                repo = dependency_mapping["repo"]
                rev = Template(dependency_mapping["rev"]).substitute(
                    rev=package["version"]
                )
                self._uv_lock[repo] = {"name": name, "rev": rev}

    def get_by_repo(self, repo: str) -> dict[str, str] | None:
        """Get a PreCommitRepo given its url.

        Args:
            repo: The repo url.

        Returns:
            A dictionary representing a repo data (name and version)
            e.g., {'name': 'black', 'rev': '22.8.0'}.
        """
        return self._uv_lock.get(repo)


def sync_repos(
    filepath: Path,
    skip: list[str] | None = None,
    config: str = YAML_FILE,
    additional_dependencies: bool = True,
    db: dict[str, dict[str, str]] = DEPENDENCY_MAPPING,
    frozen: bool = False,
) -> int:
    """Synchronize the .pre-commit-config.yaml with uv.lock file."""
    if skip is None:
        skip = []
    retv = 0

    toml = TOMLFile(filepath)
    content = toml.read()

    assert isinstance(content["package"], AoT)
    uv_items = UVItems(content["package"], skip, db)

    with Path(config).open("r") as stream:
        pre_commit_data = yaml.safe_load(stream)

    repo_pattern = []
    for repo in pre_commit_data["repos"]:
        new_repo = uv_items.get_by_repo(repo=repo["repo"])
        if "rev" in repo:  # skip `repo: local`
            repo_pattern.append(new_repo)

    with Path(config).open("r", newline="") as f:
        original = f.read()

    lines = original.splitlines(True)
    idxs = [i for i, line in enumerate(lines) if REV_LINE_RE.match(line)]
    for idx, pre_commit_repo in zip(idxs, repo_pattern, strict=False):
        if pre_commit_repo is None:
            continue

        match = REV_LINE_RE.match(lines[idx])
        assert match is not None

        lock_rev = pre_commit_repo["rev"]
        config_rev = match["rev"].replace('"', "").replace("'", "")

        if frozen and FROZEN_REV_RE.fullmatch(config_rev) and match["comment"]:
            config_rev = match["comment"]

        if lock_rev == config_rev:
            continue

        new_rev_s = yaml.dump({"rev": lock_rev}, default_style=match["quotes"])
        new_rev = new_rev_s.split(":", 1)[1].strip()

        rest = ""
        if match["rest"]:
            rest = match[5] or ""
            if match["comment"]:
                rest += "#"
            rest += match["rest"]

        lines[idx] = f"{match[1]}rev:{match[2]}{new_rev}{rest}{match['eol']}"
        retv |= 1

    if additional_dependencies:
        idxs = [i for i, line in enumerate(lines) if ADD_DEP_RE.match(line)]
        for idx in idxs:
            match = ADD_DEP_RE.match(lines[idx])
            assert match is not None
            package = match["package"].lower().replace("_", "-")
            if package not in uv_items.version:
                continue
            new_line = (
                f"{match[1]}-{match[2]}{match['quotes']}{package}"
                f"=={uv_items.version[package]}{match['quotes']}  {match['rest']}"
            ).rstrip()
            if lines[idx] != f"{new_line}{match['eol']}":
                lines[idx] = f"{new_line}{match['eol']}"
                retv |= 1

    with Path(config).open("w", newline="") as f:
        f.write("".join(lines))
    return retv


def main(argv: Sequence[str] | None = None) -> int:
    """Main function to parse arguments and call sync_repos."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    # parser.add_argument(
    #     "--all",
    #     action="store_true",
    #     help="Scan all dependencies in uv.lock (main and dev)",
    # )
    # See how to pass a list here: https://github.com/pre-commit/pre-commit/issues/971
    parser.add_argument("--skip", nargs="*", default=[], help="Packages to skip")
    parser.add_argument(
        "--config",
        type=str,
        default=YAML_FILE,
        help="Path to the .pre-commit-config.yaml file",
    )
    parser.add_argument(
        "--allow-frozen",
        action="store_true",
        dest="frozen",
        help="Trust `frozen: xxx` comments for frozen revisions. "
        "If the comment specifies the same revision as the lock file the check passes. "
        "Otherwise the revision is replaced with expected revision tag.",
    )
    parser.add_argument(
        "--skip-additional-dependencies",
        action="store_false",
        dest="additional_dependencies",
        help="Skip matching versions for hooks' additional dependencies.",
    )
    parser.add_argument(
        "--db",
        type=str,
        help="Path to a custom package list (json)",
    )
    args = parser.parse_args(argv)
    if args.db is None:
        mapping = DEPENDENCY_MAPPING
    else:
        with Path(args.db).open("r") as f:
            mapping = json.load(f)
    retv = 0
    for filename in args.filenames:
        retv |= sync_repos(
            filepath=Path(filename),
            skip=args.skip,
            config=args.config,
            additional_dependencies=args.additional_dependencies,
            db=mapping,
            frozen=args.frozen,
        )
    return retv


if __name__ == "__main__":
    raise SystemExit(main())
