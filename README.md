# Context Highlighter

A Python tool for highlighting text phrases in PDF documents using OCR or PyMuPDF-based text search.

## Features

- **Class-Based Architecture**: Extensible highlighter classes with inheritance
- **OCR Highlighter**: Find text in scanned documents with table filtering
- **PyMuPDF Highlighter**: Fast text search for searchable PDFs
- **Evaluation System**: Comprehensive mAP-based evaluation with visualization

## Usage

### OCR-Based Highlighting
```python
from src.highlighters.ocr.highlighter import OCRHighlighter

highlighter = OCRHighlighter()
results = highlighter.highlight(
    pdf_path="document.pdf",
    page_number=1,
    sentences=["Text to highlight"],
    output_path="highlighted.pdf",
    table=True,
    table_index=0
)
```

### PyMuPDF Highlighting
```python
from src.highlighters.pymupdf.highlighter import PyMuPDFHighlighter

highlighter = PyMuPDFHighlighter()
results = highlighter.highlight(
    pdf_path="document.pdf", 
    page_number=1,
    sentences=["Text to highlight"],
    output_path="highlighted.pdf"
)
```

### Evaluation
```python
from evaluation.evaluate import evaluate_highlighting_function
from src.highlighters.ocr.highlighter import OCRHighlighter
from src.config import CFG

results = evaluate_highlighting_function(
    OCRHighlighter,
    CFG.pdf_dir,
    CFG.processed_json_dir,
    table=True,
    table_index=0
)
```

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
