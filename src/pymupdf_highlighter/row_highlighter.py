import fitz  # PyMuPDF


def highlight_sentences_on_page(pdf_path, page_number, sentences, output_path=None):
    """
    Highlight multiple sentences on a specific page using simple search and highlight.
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Page number (1-indexed)
        sentences: List of sentences to highlight
        output_path: Optional path to save the highlighted PDF
        
    Returns:
        List of dictionaries with sentence and bounding box
        Format: [{'sentence': str, 'bbox': [left, top, right, bottom]}, ...]
    """
    pdf = fitz.open(pdf_path)
    
    if page_number < 1 or page_number > len(pdf):
        print(f"Invalid page number {page_number}")
        pdf.close()
        return []
    
    page = pdf[page_number - 1]
    
    # Get page dimensions for percentage conversion
    page_rect = page.rect
    page_width = page_rect.width
    page_height = page_rect.height
    
    result = []
    
    for sentence in sentences:
        quads = page.search_for(sentence)
        bbox = {}
        
        if quads:
            page.add_highlight_annot(quads)
            # Use the first found quad as the bounding box
            if quads:
                first_quad = quads[0]
                
                # Convert absolute coordinates to percentages
                x_percent = (first_quad.x0 / page_width) * 100.0
                y_percent = (first_quad.y0 / page_height) * 100.0
                width_percent = ((first_quad.x1 - first_quad.x0) / page_width) * 100.0
                height_percent = ((first_quad.y1 - first_quad.y0) / page_height) * 100.0
                
                bbox = {
                    'x': x_percent,
                    'y': y_percent,
                    'width': width_percent,
                    'height': height_percent
                }
        
        result.append({
            'sentence': sentence,
            'bbox': bbox
        })
    
    # Only save PDF if output_path is provided
    if output_path:
        pdf.save(output_path)
        print(f"Highlighted {len(sentences)} sentences on page {page_number}, saved to {output_path}")
    
    pdf.close()
    return result
