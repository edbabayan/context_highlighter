"""
Enhanced PDF Text Highlighting - Inference Module

This module provides a user-friendly example for highlighting text in PDF documents.
It demonstrates how to use the OCRHighlighter class to find and highlight specific
text content on PDF pages.

Features:
- OCR-based text detection for scanned documents
- Table filtering capabilities for targeted highlighting
- Automatic temporary file cleanup
- Easy configuration through simple variables

Author: Context Highlighter Team
Last Updated: 2025
"""

# Import required modules
from src.highlighters.ocr.highlighter import OCRHighlighter
from src.config import CFG

# ================================
# CONFIGURATION SECTION
# ================================
# Modify these variables according to your needs

# Path to your PDF file
# Replace this with the path to your actual PDF document
_pdf_path = "/Users/eduard_babayan/Documents/epam_projects/context_highlighter/Document.pdf"

# List of text/sentences you want to find and highlight
# Add or modify the text you're looking for in your PDF
sentences_to_highlight = [
    "Financial statements",
    # Add more sentences here as needed:
    # "Revenue",
    # "Total Assets", 
    # "Quarterly Report"
]

# Page number where you want to search for the text
# Note: Page numbers start from 1 (not 0)
target_page = 20

# ================================
# HIGHLIGHTING EXECUTION
# ================================

print("=" * 60)
print("PDF TEXT HIGHLIGHTING TOOL")
print("=" * 60)
print(f"📄 PDF File: {_pdf_path}")
print(f"📖 Target Page: {target_page}")
print(f"🔍 Searching for {len(sentences_to_highlight)} text(s):")
for i, sentence in enumerate(sentences_to_highlight, 1):
    print(f"   {i}. '{sentence}'")
print("=" * 60)

# Initialize the OCR-based highlighter
# This uses Optical Character Recognition to find text in scanned documents
print("🚀 Initializing OCR Highlighter...")
highlighter = OCRHighlighter()

# Perform the highlighting operation
print("⚡ Starting text highlighting process...")

boxes = highlighter.highlight(
    pdf_path=_pdf_path,
    page_number=target_page,
    sentences=sentences_to_highlight,
    output_path=CFG.inference_pdf_path,
    table=True,      # Enable table-based filtering
    table_index=0    # Use first table (index 0)
)

# ================================
# RESULTS ANALYSIS
# ================================

print("\n" + "=" * 60)
print("✅ HIGHLIGHTING COMPLETED!")
print("=" * 60)

# Count successful matches
found_texts = [item for item in boxes if item.get('bbox')]
not_found_texts = [item for item in boxes if not item.get('bbox')]

print(f"📊 RESULTS SUMMARY:")
print(f"   • Total texts searched: {len(sentences_to_highlight)}")
print(f"   • Texts found and highlighted: {len(found_texts)}")
print(f"   • Texts not found: {len(not_found_texts)}")
print(f"   • Success rate: {len(found_texts)/len(sentences_to_highlight)*100:.1f}%")