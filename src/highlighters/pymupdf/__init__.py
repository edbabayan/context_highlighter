"""
PyMuPDF-based highlighter package.

This package provides text highlighting functionality using PyMuPDF's built-in
text search capabilities for fast and accurate text location.
"""

from .highlighter import PyMuPDFHighlighter, highlight_sentences_on_page

__all__ = ['PyMuPDFHighlighter', 'highlight_sentences_on_page']