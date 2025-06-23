# Context Highlighter

A Python tool for precisely highlighting text phrases within specific tables in PDF documents.

## Overview

This project solves the challenge of highlighting text in complex PDF documents with multiple tables on the same page. Instead of highlighting all occurrences of a phrase, it allows you to target specific tables by their position.

## Key Features

- **Table Detection**: Automatically extracts and indexes all tables from PDF documents
- **Position-Based Indexing**: Tables are sorted by position (top-to-bottom, then left-to-right)
- **Precise Highlighting**: Highlight phrases only within specified tables
- **Visual Feedback**: Shows table positions and indices for easy targeting

## How It Works

1. **Extract Tables**: The system scans your PDF and identifies all tables with their positions
2. **Index by Position**: Tables are numbered starting from 0 (top-left table = index 0)
3. **Target & Highlight**: Specify which table to search in and highlight your phrase

## Quick Start

### 1. Extract Tables from PDF
```python
from src.table_extractor import extract_tables_from_pdf
from src.config import CFG

extract_tables_from_pdf("your_document.pdf", CFG.tables_dir)
```

### 2. View Available Tables
```python
from src.highlighters.row_highlighter import get_table_info_for_page

# See all tables on page 17
get_table_info_for_page(CFG.tables_dir, page_number=17)
```

Output:
```
Found 2 table(s) on page 17:
  Table 0: Top=676.1, Left=24.6 (BOTTOMLEFT)
  Table 1: Top=540.7, Left=24.3 (BOTTOMLEFT)
```

### 3. Highlight Phrase in Specific Table
```python
from src.highlighters.row_highlighter import highlight_phrase_in_table

highlight_phrase_in_table(
    pdf_path="your_document.pdf",
    output_path="highlighted_document.pdf", 
    page_number=17,
    phrase="Financial statements",
    table_index=0,  # Target the first (top) table
    tables_json_path=CFG.tables_dir
)
```

## Table Indexing System

Tables are automatically indexed by their visual position:

- **Page 17 with 2 tables**:
  - `table_index=0` → Top table
  - `table_index=1` → Bottom table

- **Page 20 with 2 side-by-side tables**:
  - `table_index=0` → Left table
  - `table_index=1` → Right table

## Project Structure

```
src/
├── table_extractor.py      # Extract and sort tables from PDF
├── highlighters/
│   └── row_highlighter.py  # Highlight phrases in specific tables
├── config.py              # Configuration settings
└── testing.py             # Example usage
```

## Configuration

Update `src/config.py` with your file paths:
```python
class CFG:
    tables_dir = "tables.json"
    row_highlighter_pdf_path = "highlighted_output.pdf"
```

## Use Cases

- **Financial Reports**: Highlight specific values in income statements vs balance sheets
- **Research Papers**: Target data in specific tables when multiple tables exist
- **Legal Documents**: Highlight clauses in specific contract sections
- **Academic Papers**: Focus on results in particular data tables

## Requirements

- Python 3.7+
- PyMuPDF (fitz)
- docling

## Installation

```bash
pip install pymupdf docling
```

---

*This tool ensures you highlight the right information in the right table, every time.*
