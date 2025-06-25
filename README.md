# Context Highlighter

A Python tool for highlighting text phrases in PDF documents using two different approaches: standard text search and OCR-based highlighting.

## Overview

This project provides flexible text highlighting capabilities for PDF documents. You can choose between standard text search (for searchable PDFs) or OCR-based highlighting (for scanned PDFs or images).

## Key Features

- **Dual Highlighting Methods**: Choose between standard text search or OCR-based highlighting
- **Simple Interface**: Same function signature for both methods
- **OCR Fuzzy Matching**: Handles OCR errors with intelligent text matching
- **Flexible Input**: Works with both searchable and scanned PDFs

## Highlighting Methods

### Method 1: Standard Text Search
Best for searchable PDFs with selectable text.

```python
from src.highlighters.row_highlighter import highlight_sentences_on_page
from src.config import CFG

sentences_to_highlight = [
    "Financial statements",
    "Total revenue"
]

highlight_sentences_on_page(
    pdf_path="document.pdf",
    output_path="highlighted.pdf",
    page_number=17,
    sentences=sentences_to_highlight
)
```

### Method 2: OCR-Based Highlighting
Best for scanned PDFs or images where text is not selectable.

```python
from src.ocr_highlighter.ocr_highlighter import highlight_sentences_with_ocr
from src.config import CFG

sentences_to_highlight = [
    "Financial statements",
    "Total revenue"
]

highlight_sentences_with_ocr(
    pdf_path="scanned_document.pdf",
    output_path="highlighted_ocr.pdf",
    page_number=17,
    sentences=sentences_to_highlight
)
```

## Quick Start

### Standard Highlighting (Searchable PDFs)
```python
from src.highlighters.row_highlighter import highlight_sentences_on_page
from src.config import CFG

highlight_sentences_on_page(
    "/path/to/document.pdf", 
    CFG.row_highlighter_pdf_path,
    page_number=17,
    sentences=["Text to highlight"]
)
```

### OCR Highlighting (Scanned PDFs)
```python
from src.ocr_highlighter.ocr_highlighter import highlight_sentences_with_ocr
from src.config import CFG

highlight_sentences_with_ocr(
    "/path/to/document.pdf",
    CFG.root.joinpath("highlighted_ocr.pdf"),
    page_number=17,
    sentences=["Text to highlight"]
)
```

## Project Structure

```
src/
├── highlighters/
│   └── row_highlighter.py     # Standard text search highlighting
├── ocr_highlighter/
│   └── ocr_highlighter.py     # OCR-based highlighting
├── config.py                  # Configuration settings
├── testing.py                 # Standard highlighter testing
├── ocr_testing.py             # OCR highlighter testing
└── table_extractor.py         # Table extraction utilities
```

## OCR Features

The OCR highlighter includes:
- **Fuzzy Matching**: Handles OCR recognition errors
- **Word Sequence Matching**: Finds partial sentence matches
- **Confidence Filtering**: Only uses high-confidence OCR results
- **Bounding Box Creation**: Creates precise highlight regions

## Use Cases

### Standard Highlighter
- **Digital PDFs**: Documents with selectable text
- **Reports**: Well-formatted business documents
- **Articles**: Text-based publications

### OCR Highlighter  
- **Scanned Documents**: Image-based PDFs
- **Old Documents**: Legacy files without searchable text
- **Photos**: Screenshots or photos of documents
- **Mixed Content**: PDFs with both text and image elements

## Requirements

- Python 3.7+
- PyMuPDF
- pytesseract
- Pillow

## Installation

```bash
pip install -r requirements.txt
```

## Testing

Test standard highlighting:
```bash
python src/testing.py
```

Test OCR highlighting:
```bash
python src/ocr_testing.py
```

---

*Choose the right highlighting method for your document type.*
