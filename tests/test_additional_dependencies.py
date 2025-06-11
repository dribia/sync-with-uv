"""Test additional dependencies handling in sync_with_uv."""

from pathlib import Path

import pytest

from sync_with_uv import main
from tests.helpers import (
    CONFIG_CONTENT,
    LOCK_CONTENT,
)

LEN_CONFIG_CONTENT = CONFIG_CONTENT.count("\n")


# fmt: off
@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            {},
            {
                "- foobarbaz>=0.9,<1\n": False,
                "- foobarbaz>=0.9,<1  # comment\n": False,
                "- FOOBARBAZ>=0.9,<1\n": False,
                "- foobarbaz==1.0.1\n": True,
            },
        ),
        (
            {"additional_dependencies": False},
            {
                "- foobarbaz>=0.9,<1\n": True,
                "- foobarbaz>=0.9,<1  # comment\n": True,
                "- FOOBARBAZ>=0.9,<1\n": True,
                "- foobarbaz==1.0.1\n": False,
            },
        ),
    ],
)
# fmt: on
def test_sync_repos(tmpdir: Path, test_input: dict, expected: dict) -> None:
    """Test repo synchronization against different inputs and configurations."""
    lock_file = tmpdir / "uv.lock"
    with lock_file.open("w") as f:
        f.write(LOCK_CONTENT)
    config_file = tmpdir / ".pre-commit-yaml"
    with config_file.open("w") as f:
        f.write(CONFIG_CONTENT)

    retv = main.sync_repos(lock_file, **test_input, config=str(config_file))

    with config_file.open("r") as f:
        all_lines = f.read()

    for dependency, in_file in expected.items():
        assert (dependency in all_lines) is in_file

    with config_file.open("r") as f:
        lines = f.readlines()
    assert len(lines) == LEN_CONFIG_CONTENT
    assert retv == 1
