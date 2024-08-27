from verification_digit_pty.plugins import _PLUGINS


def test_plugin_register_plugin() -> None:
    from verification_digit_pty.plugins import register_plugin

    @register_plugin
    def f() -> str:
        return "f"

    assert f() == "f"
    assert "tests.unit.test_plugins.f" in _PLUGINS
