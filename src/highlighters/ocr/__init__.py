"""
OCR-based highlighter package.

This package provides text highlighting functionality using OCR (Optical Character Recognition)
to locate text positions in PDF documents, with optional table filtering capabilities.
"""

from .highlighter import OCRHighlighter

__all__ = ['OCRHighlighter']