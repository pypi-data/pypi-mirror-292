import os
import streamlit.components.v1 as components
from typing import Callable, Optional

_RELEASE = True


if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_tree_independent_components",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_tree_independent_components", path=build_dir)


def tree_independent_components(treeItems={},checkItems=[], disable=False,on_change: Optional[Callable[[], None]] = None,key=None):

    component_value = _component_func(treeItems=treeItems,checkItems=checkItems, disable=disable, on_change=on_change, key=key, default=checkItems)
    if on_change is not None:
        on_change()
    return component_value


