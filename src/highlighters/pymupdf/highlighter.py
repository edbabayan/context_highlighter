from typing import List, Dict, Any, Optional

import fitz  # PyMuPDF

from src.highlighters.base import Highlighter


class PyMuPDFHighlighter(Highlighter):
    """
    Highlighter implementation using PyMuPDF's built-in text search functionality.
    """
    
    def highlight(self, pdf_path: str, page_number: int, sentences: List[str], 
                 output_path: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Highlight multiple sentences on a specific page using simple search and highlight.
        
        Args:
            pdf_path: Path to the PDF file
            page_number: Page number (1-indexed)
            sentences: List of sentences to highlight
            output_path: Optional path to save the highlighted PDF
            
        Returns:
            List of dictionaries with sentence and bounding box
            Format: [{'sentence': str, 'bbox': {'x': %, 'y': %, 'width': %, 'height': %}}, ...]
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
            
            if quads:
                page.add_highlight_annot(quads)
                # Return all found instances of the sentence
                for quad in quads:
                    # Convert absolute coordinates to percentages
                    x_percent = (quad.x0 / page_width) * 100.0
                    y_percent = (quad.y0 / page_height) * 100.0
                    width_percent = ((quad.x1 - quad.x0) / page_width) * 100.0
                    height_percent = ((quad.y1 - quad.y0) / page_height) * 100.0
                    
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
            else:
                # If no matches found, still add entry with empty bbox for consistency
                result.append({
                    'sentence': sentence,
                    'bbox': {}
                })
        
        # Only save PDF if output_path is provided
        if output_path:
            pdf.save(output_path)
            print(f"Highlighted {len(sentences)} sentences on page {page_number}, saved to {output_path}")
        
        pdf.close()
        return result


def highlight_sentences_on_page(pdf_path, page_number, sentences, output_path=None):
    """Legacy function wrapper for backward compatibility."""
    highlighter = PyMuPDFHighlighter()
    return highlighter.highlight(pdf_path, page_number, sentences, output_path)
