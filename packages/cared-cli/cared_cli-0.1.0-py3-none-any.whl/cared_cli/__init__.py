"""
A command line interface for managing a CaReD server.

Copyright David Linke 2024
"""

try:
    from cared_cli._version import __version__, __version_tuple__
except ImportError:  # pragma: no cover
    # package is not installed
    __version__ = "0.0.0"
    __version_tuple__ = (0, 0, 0)
