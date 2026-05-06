"""Tests for the GiantContext SDK."""


from giantcontext import GiantContext, GiantContextConfig, create_giant_context


def test_create_giant_context():
    """Test creating an SDK instance."""
    gc = create_giant_context(api_key="gct_test_key")
    assert isinstance(gc, GiantContext)


def test_config_defaults():
    """Test configuration defaults."""
    config = GiantContextConfig(api_key="gct_test")
    assert config.api_key == "gct_test"
    assert config.base_url == "https://api.giantcontext.com"
    assert config.timeout == 30.0


def test_config_custom():
    """Test custom configuration."""
    config = GiantContextConfig(
        api_key="gct_test",
        base_url="https://custom.api.com",
        timeout=60.0,
    )
    assert config.api_key == "gct_test"
    assert config.base_url == "https://custom.api.com"
    assert config.timeout == 60.0


def test_resources_exist():
    """Test that resource classes are accessible."""
    gc = create_giant_context(api_key="gct_test")
    # Check some common resources exist
    assert hasattr(gc, "projects")
    assert hasattr(gc, "chat")
    assert hasattr(gc, "me")
