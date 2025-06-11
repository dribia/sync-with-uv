"""Test parsing of the uv.lock file and UVItems class."""

import tomlkit

from sync_with_uv.main import UVItems
from tests.helpers import LOCK_CONTENT


def test_uv_items_creation() -> None:
    """Test UVItems init."""
    content = tomlkit.loads(LOCK_CONTENT)
    assert isinstance(content["package"], tomlkit.items.AoT)
    p = UVItems(content["package"])
    assert type(p._uv_lock) is dict


def test_uv_items_metadata() -> None:
    """Test PreCommitRepo metadata (returned by UVItems.get_by_repo)."""
    content = tomlkit.loads(LOCK_CONTENT)
    assert isinstance(content["package"], tomlkit.items.AoT)
    p = UVItems(content["package"])
    item = p.get_by_repo("https://github.com/pre-commit/mirrors-mypy")
    assert type(item) is dict
    assert item["name"] == "mypy"
    assert item["rev"] == "v0.910"
