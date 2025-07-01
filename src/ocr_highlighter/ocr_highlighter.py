import re
import json
import difflib
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from loguru import logger

from src.config import CFG
from src.ocr_highlighter.table_extractor import extract_tables_from_pdf


def highlight_sentences_with_ocr(pdf_path, page_number, sentences, table=True, table_index=0, output_path=None):
    """
    Highlight multiple sentences on a specific page using OCR to find text locations.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the highlighted PDF
        page_number: Page number (1-indexed)
        sentences: List of sentences to highlight
        table: Boolean flag to enable table-based filtering
        table_index: Index of the table to filter by (0-indexed)
        
    Returns:
        List of dictionaries with sentence and bounding box
        Format: [{'sentence': str, 'bbox': [left, top, right, bottom]}, ...]
    """
    pdf = fitz.open(pdf_path)

    CFG.temp_dir.mkdir(parents=True, exist_ok=True)

    if page_number < 1 or page_number > len(pdf):
        logger.error(f"Invalid page number {page_number}")
        pdf.close()
        return []
    
    page = pdf[page_number - 1]
    
    # Convert page to image for OCR
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for better OCR
    img_data = pix.tobytes("png")
    image = Image.open(fitz.io.BytesIO(img_data))
    
    # Get OCR data with bounding boxes
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    # Scale factor to convert from image coordinates back to PDF coordinates
    scale_factor = 0.5  # Since we scaled up by 2x for OCR
    
    # Extract tables if table filtering is enabled
    table_bbox = None
    if table:
        # Extract the specific page and save as new PDF to CFG's temp path
        temp_pdf = fitz.open()
        temp_pdf.insert_pdf(pdf, from_page=page_number-1, to_page=page_number-1)
        temp_pdf.save(CFG.temp_pdf_path)
        temp_pdf.close()
        
        # Extract tables from the single-page PDF
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            extract_tables_from_pdf(CFG.temp_pdf_path, Path(tmp_file.name))
            
        with open(tmp_file.name, 'r') as f:
            tables_data = json.load(f)
            
        if tables_data and table_index < len(tables_data):
            selected_table = tables_data[table_index]
            table_bbox = selected_table['bbox']
    
    result = []
    
    for sentence in sentences:
        # Find sentence in OCR text using fuzzy matching
        found_boxes = _find_sentence_boxes(sentence, ocr_data, scale_factor, table_bbox)
        
        # Remove duplicate boxes
        unique_boxes = []
        for box in found_boxes:
            if box not in unique_boxes:
                unique_boxes.append(box)
        
        # Add all unique boxes to results, not just the first one
        if unique_boxes:
            for box in unique_boxes:
                result.append({
                    'sentence': sentence,
                    'bbox': box
                })
                
                # Convert box coordinates to PyMuPDF quad
                quad = fitz.Quad(
                    fitz.Point(box[0], box[1]),  # top-left
                    fitz.Point(box[2], box[1]),  # top-right
                    fitz.Point(box[0], box[3]),  # bottom-left
                    fitz.Point(box[2], box[3])   # bottom-right
                )
                page.add_highlight_annot(quad)
        else:
            # If no matches found, still add entry with empty bbox for consistency
            result.append({
                'sentence': sentence,
                'bbox': []
            })
    
    pdf.save(output_path)
    pdf.close()
    logger.success(f"Highlighted text regions using OCR on page {page_number}, saved to {output_path}")
    return result


def _find_sentence_boxes(sentence, ocr_data, scale_factor, table_bbox=None):
    """
    Find bounding boxes for a sentence in OCR data using fuzzy matching.
    
    Args:
        sentence: The sentence to find
        ocr_data: OCR data from pytesseract
        scale_factor: Scale factor to convert image coords to PDF coords
        table_bbox: Optional table bounding box to filter words within
        
    Returns:
        List of bounding boxes as [left, top, right, bottom]
    """
    # Clean and normalize the sentence
    sentence_clean = re.sub(r'\s+', ' ', sentence.strip().lower())
    words = sentence_clean.split()
    
    if not words:
        return []
    
    boxes = []
    text_blocks = []
    
    # Build text blocks from OCR data
    for i in range(len(ocr_data['text'])):
        if int(ocr_data['conf'][i]) > 30:  # Confidence threshold
            word = ocr_data['text'][i].strip()
            if word:
                left = ocr_data['left'][i] * scale_factor
                top = ocr_data['top'][i] * scale_factor
                width = ocr_data['width'][i] * scale_factor
                height = ocr_data['height'][i] * scale_factor
                
                # Filter by table bbox if provided
                if table_bbox is not None:
                    word_right = left + width
                    word_bottom = top + height
                    
                    # Check if word is within table bounds
                    if not (left >= table_bbox['l'] and top >= table_bbox['t'] and 
                           word_right <= table_bbox['r'] and word_bottom <= table_bbox['b']):
                        continue
                
                text_blocks.append({
                    'word': word.lower(),
                    'left': left,
                    'top': top,
                    'width': width,
                    'height': height
                })
    
    # Find sequences of words that match the sentence
    for start_idx in range(len(text_blocks)):
        # Try to match starting from this position
        matched_blocks = []
        word_idx = 0
        
        for block_idx in range(start_idx, len(text_blocks)):
            if word_idx >= len(words):
                break
                
            block = text_blocks[block_idx]
            target_word = words[word_idx]
            
            # Use exact matching for numeric values, fuzzy matching for text
            if re.match(r'^\d+\.?\d*$', target_word):  # If target is numeric
                match = block['word'] == target_word
            else:  # Use fuzzy matching for text
                similarity = difflib.SequenceMatcher(None, block['word'], target_word).ratio()
                match = similarity > 0.8  # 80% similarity threshold
            
            if match:
                matched_blocks.append(block)
                word_idx += 1
            elif matched_blocks:  # If we had matches but this doesn't match, stop
                break
        
        # If we matched most of the words, create a bounding box
        if len(matched_blocks) >= len(words) * 0.7:  # At least 70% of words matched
            if matched_blocks:
                # Create bounding box around all matched words
                left = min(block['left'] for block in matched_blocks)
                top = min(block['top'] for block in matched_blocks)
                right = max(block['left'] + block['width'] for block in matched_blocks)
                bottom = max(block['top'] + block['height'] for block in matched_blocks)
                
                boxes.append([left, top, right, bottom])
    
    return boxes