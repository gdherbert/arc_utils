# -*- coding: utf-8 -*-
"""Shared input coercion helpers for arc_utils."""
from __future__ import absolute_import

import os
import arcpy


def _normalize_to_sequence(values):
    """Return a list from single or multi-value inputs.

    Strings and path-like values are treated as a single item.
    """
    if isinstance(values, (list, tuple, set)):
        return list(values)
    return [values]


def _to_path_str(value):
    """Convert path-like values to str where possible."""
    if value is None:
        return None
    try:
        value = os.fspath(value)
    except TypeError:
        return None
    if isinstance(value, bytes):
        value = value.decode()
    return value


def _resolve_dataset_path(value, arg_name="value"):
    """Resolve supported dataset inputs to a path string.

    Supported inputs:
    - str and pathlib.Path / os.PathLike
    - ArcGIS Pro layer-name strings (resolved via arcpy.Describe(...).catalogPath)
    - objects exposing .path (wrapper objects)
    - ArcGIS Pro map/layer objects exposing .catalogPath or .dataSource
    """
    def _resolve_candidate(candidate):
        """Resolve map layer names and object references to catalog paths."""
        try:
            desc = arcpy.Describe(candidate)
            if hasattr(desc, "catalogPath") and desc.catalogPath:
                return os.path.abspath(desc.catalogPath)
        except Exception:
            pass
        return os.path.abspath(candidate)

    for attr in ("path", "catalogPath", "dataSource"):
        if hasattr(value, attr):
            candidate = _to_path_str(getattr(value, attr))
            if candidate:
                return _resolve_candidate(candidate)

    direct = _to_path_str(value)
    if direct:
        return _resolve_candidate(direct)

    raise TypeError("{} must be a path-like string or object with a valid path".format(arg_name))


def _resolve_aprx_path(value, arg_name="value"):
    """Resolve Aprx path input, preserving CURRENT special value."""
    direct = _to_path_str(value)
    if isinstance(direct, str) and direct.upper() == "CURRENT":
        return "CURRENT"

    for attr in ("path", "catalogPath", "dataSource"):
        if hasattr(value, attr):
            candidate = _to_path_str(getattr(value, attr))
            if isinstance(candidate, str) and candidate.upper() == "CURRENT":
                return "CURRENT"
            if candidate:
                return os.path.abspath(candidate)

    if direct:
        return os.path.abspath(direct)

    raise TypeError("{} must be a path-like string or object with a valid path".format(arg_name))


def _ensure_valid_path(path):
    """Validate ArcGIS path-like input and raise a consistent error."""
    if not arcpy.Exists(path):
        raise ValueError("invalid path")
    return path


def _input_display_name(value, default_name=None):
    """Best-effort human-readable name for logs and worksheet names."""
    for attr in ("name",):
        if hasattr(value, attr):
            candidate = getattr(value, attr)
            if candidate:
                return str(candidate)

    for attr in ("path", "catalogPath", "dataSource"):
        if hasattr(value, attr):
            candidate = getattr(value, attr)
            if candidate:
                return str(candidate)

    if default_name is not None:
        return str(default_name)
    return str(value)