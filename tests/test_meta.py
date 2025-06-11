"""Test version of the sync_with_uv package."""

from sync_with_uv import __version__


def test_version() -> None:
    """Test version."""
    assert __version__ == "0.1.0"
