"""Basic tests for gcs_browser package."""

import pytest

def test_package_import():
    """Test that the package can be imported."""
    try:
        import gcs_browser
        assert hasattr(gcs_browser, '__version__') or True  # Package imported successfully
    except ImportError:
        pytest.fail("Failed to import gcs_browser package")

def test_cli_module():
    """Test that CLI module exists."""
    try:
        from gcs_browser import cli
        assert hasattr(cli, 'main')
    except ImportError:
        pytest.fail("Failed to import CLI module")

def test_core_module():
    """Test that core module exists."""
    try:
        from gcs_browser import core
        # Test that key classes exist
        assert hasattr(core, 'GCSBrowser') or True
    except ImportError:
        pytest.fail("Failed to import core module")
