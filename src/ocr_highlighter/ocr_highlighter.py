import re
import difflib

import fitz  # PyMuPDF
import pytesseract
from PIL import Image


def highlight_sentences_with_ocr(pdf_path, output_path, page_number, sentences):
    """
    Highlight multiple sentences on a specific page using OCR to find text locations.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the highlighted PDF
        page_number: Page number (1-indexed)
        sentences: List of sentences to highlight
    """
    pdf = fitz.open(pdf_path)
    
    if page_number < 1 or page_number > len(pdf):
        print(f"Invalid page number {page_number}")
        pdf.close()
        return
    
    page = pdf[page_number - 1]
    
    # Convert page to image for OCR
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for better OCR
    img_data = pix.tobytes("png")
    image = Image.open(fitz.io.BytesIO(img_data))
    
    # Get OCR data with bounding boxes
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    # Scale factor to convert from image coordinates back to PDF coordinates
    scale_factor = 0.5  # Since we scaled up by 2x for OCR
    
    highlighted_count = 0
    
    for sentence in sentences:
        # Find sentence in OCR text using fuzzy matching
        found_boxes = _find_sentence_boxes(sentence, ocr_data, scale_factor)
        
        for box in found_boxes:
            # Convert box coordinates to PyMuPDF quad
            quad = fitz.Quad(
                fitz.Point(box[0], box[1]),  # top-left
                fitz.Point(box[2], box[1]),  # top-right
                fitz.Point(box[0], box[3]),  # bottom-left
                fitz.Point(box[2], box[3])   # bottom-right
            )
            page.add_highlight_annot(quad)
            highlighted_count += 1
    
    pdf.save(output_path)
    pdf.close()
    print(f"Highlighted text regions using OCR on page {page_number}, saved to {output_path}")


def _find_sentence_boxes(sentence, ocr_data, scale_factor):
    """
    Find bounding boxes for a sentence in OCR data using fuzzy matching.
    
    Args:
        sentence: The sentence to find
        ocr_data: OCR data from pytesseract
        scale_factor: Scale factor to convert image coords to PDF coords
        
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
                text_blocks.append({
                    'word': word.lower(),
                    'left': ocr_data['left'][i] * scale_factor,
                    'top': ocr_data['top'][i] * scale_factor,
                    'width': ocr_data['width'][i] * scale_factor,
                    'height': ocr_data['height'][i] * scale_factor
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
            
            # Use fuzzy matching for individual words
            similarity = difflib.SequenceMatcher(None, block['word'], target_word).ratio()
            
            if similarity > 0.8:  # 80% similarity threshold
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