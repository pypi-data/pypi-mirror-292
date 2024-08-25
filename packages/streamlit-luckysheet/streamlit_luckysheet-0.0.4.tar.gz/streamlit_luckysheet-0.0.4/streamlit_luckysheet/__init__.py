import os
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_luckysheet",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_luckysheet", path=build_dir)

def streamlit_luckysheet(name="",height=0, encodedFile=None, key="", default=0):
    component_value = _component_func(name=name,height=height, encodedFile=encodedFile, key=key, default=default)
    return component_value
