"""
Highlighters package for PDF text highlighting functionality.

This package provides a base abstract class and implementations for different
text highlighting strategies.
"""

from .base import Highlighter
from .ocr.highlighter import OCRHighlighter
from .pymupdf.highlighter import PyMuPDFHighlighter

__all__ = ['Highlighter', 'OCRHighlighter', 'PyMuPDFHighlighter']