# Sync with uv

[![CI](https://github.com/dribia/sync-with-uv/actions/workflows/ci.yml/badge.svg)](https://github.com/dribia/sync-with-uv/actions/workflows/ci.yml)
[![codecov](https://img.shields.io/codecov/c/github/dribia/sync-with-uv?color=%2334D058)](https://codecov.io/gh/dribia/sync-with-uv)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/dribia/sync-with-uv/main.svg)](https://results.pre-commit.ci/latest/github/dribia/sync-with-uv/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A pre-commit hook for keeping in sync the repos `rev` in
`.pre-commit-config.yaml` with the packages version locked into `uv.lock`. Check
out [pre-commit.com](https://pre-commit.com/) for more about the main framework.

> [!IMPORTANT]
> This repository is strongly inspired in
> [sync_with_poetry](https://github.com/floatingpurr/sync_with_poetry).

## What problem does this hook help us solve?

When using `uv`, the package versions are locked in a file named `uv.lock`. This
file contains the exact versions of the packages used in the project, ensuring
that the same versions are used across environments. However, the
`.pre-commit-config.yaml` file, which defines the pre-commit hooks and their
repositories, may not always reflect the latest versions of the packages as
specified in `uv.lock`.

This hook helps us keep the `rev` of each `repo` in `.pre-commit-config.yaml` in
sync with the corresponding package version stored in `uv.lock`.

E.g., starting from the following files:

```toml
# uv.lock
[[package]]
name = "mypy"
version = "1.16.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [ ... ]
sdist = { ... }
wheels = [ ... ]
```

```yaml
# .pre-commit-config.yaml
repos:
  # mypy - static type checker
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.15.1
    hooks:
      - id: mypy
```

this hook will bump `mypy` in `.pre-commit-config.yaml` as follows:

```yaml
# .pre-commit-config.yaml
repos:
  # mypy - static type checker
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.16.0
    hooks:
      - id: mypy
```

### Additional dependencies

Some pre-commit hooks may have additional dependencies with their own
constraints. For example, the `mypy` hook may have an additional dependency on
`pydantic`. This hook will sync those additional dependencies as well, ensuring
that the versions of the additional dependencies are also in sync with the
versions specified in `uv.lock`.

## Usage

Excerpt from a `.pre-commit-config.yaml` using an example of this hook:

```yaml
- repo: https://github.com/dribia/sync-with-uv
  rev: "" # the revision or tag to clone at
  hooks:
    - id: sync-with-uv
      args: [] # optional args
```

### Args

```
  --skip [SKIP ...]  Packages to skip
  --config CONFIG    Path to a custom .pre-commit-config.yaml file
  --db PACKAGE_LIST  Path to a custom package list (json)
  --allow-frozen     Trust `frozen: xxx` comments for frozen revisions.
  --skip-additional-dependencies
                    Skip matching versions for packages in hooks' additional dependencies.
```

Usually this hook uses only dev packages to sync the hooks. Pass `--all`, if you
want to scan also the main project packages.

Pass `--skip <package_1> <package_2> ...` to disable the automatic
synchronization of the repos such packages correspond to.

Pass `--config <config_file>` to point to an alternative config file (it
defaults to `.pre-commit-config.yaml`).

Pass `--db <package_list_file>` to point to an alternative package list (json).
Such a file overrides the mapping in [`db.py`](sync_with_poetry/db.py).

Pass `--allow-frozen` if you want to use frozen revisions in your config.
Without this option _SWP_ will replace frozen revisions with the tag name taken
from `poetry.lock` even if the frozen revision specifies the same commit as the
tag. This options relies on `frozen: xxx` comments appended to the line of the
frozen revision where `xxx` will be the tag name corresponding to the commit
hash used. If the comment specifies the same revision as the lock file nothing
is changed. Otherwise, the revision is replaced with the expected revision tag
and the `frozen: xxx` comment is removed.

Pass `--skip-additional-dependencies` to skip matching versions for packages in
hooks' additional dependencies.

## Supported packages

Supported packages out-of-the-box are listed in [`db.py`](sync-with-uv/db.py):

- autopep8
- bandit
- black
- commitizen
- flake8
- flakeheaven
- isort
- mypy
- pyupgrade
- ruff
- deptry
- licenseheaders
- sqlfluff

You can create your very own package list, passing a custom json file with the
arg `--db`. Such a file specifies how to map a package to the corresponding
repo, following this pattern:

```json
{
  "<package_name_in_PyPI>": {
    "repo": "<repo_url_for_the_package>",
    "rev": "<revision_template>"
  }
}
```

Sometimes the template of the version number of a package in PyPI differs from
the one used in the repo `rev`. For example, version `0.910` of `mypy` in PyPI
(no pun intended) maps to repo `rev: v0.910`. To make this hook aware of the
leading `v`, you need to specify `"v${rev}"` as a `"<revision_template>"`. Use
`"${rev}"` if both the package version and the repo `rev` follow the same
pattern.

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md).

## Credits

This hook is inspired by
[sync_with_poetry](https://github.com/floatingpurr/sync_with_poetry).
