import inspect
from typing import Any, Callable

_PLUGINS = {}


def get_plugin(plugin: str) -> Callable[..., Any]:
    plugins_found = []
    for key in _PLUGINS:
        if plugin in key:
            plugins_found.append(_PLUGINS[key])
    if len(plugins_found) == 1:
        return plugins_found[0]
    elif len(plugins_found) > 1:
        raise ValueError(f"Plugin {plugin} is ambiguous")
    else:
        raise ValueError(f"Plugin {plugin} not found")


def register_plugin(func: Callable[..., Any]) -> Callable[..., Any]:
    module = get_module_name(func)
    plugin_key = f"{module}.{func.__name__}"
    if plugin_key in _PLUGINS:
        raise ValueError(f"Plugin {plugin_key} already registered")
    _PLUGINS[plugin_key] = func
    return func


def get_module_name(func):
    return inspect.getmodule(func).__name__
