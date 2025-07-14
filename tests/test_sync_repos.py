"""Test synchronization of repositories with `sync_repos` function."""

from pathlib import Path

import pytest

from sync_with_uv import main
from tests.helpers import (
    CONFIG_CONTENT,
    CUSTOM_DEPENDENCY_MAPPING,
    LOCK_CONTENT,
    get_repo_version,
)

LEN_CONFIG_CONTENT = CONFIG_CONTENT.count("\n")


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # sync all dependencies
        (
            {"skip": []},
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.910",  # bumped
                "https://github.com/pycqa/flake8": "4.0.1",  # bumped
                "https://github.com/psf/black": "21.11b1",  # bumped
                "https://github.com/pycqa/isort": "5.10.1",  # not managed by uv
            },
        ),
        # sync dependencies, skipping `flake8` and black
        (
            {"skip": ["black", "flake8"]},
            {
                "https://github.com/pre-commit/mirrors-mypy": "v0.910",  # bumped
                "https://github.com/pycqa/flake8": "3.9.0",  # not bumped skipped
                "https://github.com/psf/black": "20.8b1",  # not bumped skipped
                "https://github.com/pycqa/isort": "5.10.1",  # not managed by uv
            },
        ),
        # sync all dependencies from custom mapping
        (
            {"skip": [], "db": CUSTOM_DEPENDENCY_MAPPING},
            {
                "https://example.org/fakepackages/foobarbaz": "1.0.1",  # bumped (main)
            },
        ),
    ],
)
def test_sync_repos(tmpdir: Path, test_input: dict, expected: dict) -> None:
    """Test repo synchronization against different inputs and configurations."""
    lock_file = tmpdir / "uv.lock"
    with lock_file.open("w") as f:
        f.write(LOCK_CONTENT)
    config_file = tmpdir / ".pre-commit-yaml"
    with config_file.open("w") as f:
        f.write(CONFIG_CONTENT)

    retv = main.sync_repos(lock_file, **test_input, config=str(config_file))

    for repo in expected:
        assert get_repo_version(config_file, repo) == expected[repo]

    with config_file.open("r") as f:
        lines = f.readlines()
    assert len(lines) == LEN_CONFIG_CONTENT
    assert retv == 1


def test_no_change(tmpdir: Path) -> None:
    """Test a run without updates."""
    lock_file = tmpdir / "uv.lock"
    with lock_file.open("w") as f:
        f.write(LOCK_CONTENT)
    config_file = tmpdir / ".pre-commit-yaml"
    with config_file.open("w") as f:
        f.write(CONFIG_CONTENT)
    retv = main.sync_repos(
        lock_file,
        skip=["mypy", "flake8", "black"],
        additional_dependencies=False,
        config=str(config_file),
    )
    assert retv == 0
