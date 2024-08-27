"""
pywebinfo: A Python module extract basic webpage information.

This module provides a simple way to extract metadata (title, description, image, favicon) from web pages.

Classes:
    PyWebInfo: Main class for fetching and parsing webpage information.

Example:
    >>> from pywebinfo import PyWebInfo
    >>> info = PyWebInfo('https://example.com')
    >>> print(info.url)
    >>> print(info.title)
    >>> print(info.description)
    >>> print(info.image)
    >>> print(info.favicon)
"""


__all__ = ['PyWebInfo']


from .main import PyWebInfo