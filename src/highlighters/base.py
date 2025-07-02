from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class Highlighter(ABC):
    """
    Base template class for PDF text highlighting functionality.
    
    All highlighter implementations should inherit from this class and implement
    the highlight() method with their specific highlighting logic.
    """
    
    @abstractmethod
    def highlight(self, pdf_path: str, page_number: int, sentences: List[str], 
                 output_path: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Highlight sentences on a specific page of a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            page_number: Page number (1-indexed)
            sentences: List of sentences to highlight
            output_path: Optional path to save the highlighted PDF
            **kwargs: Additional arguments specific to each implementation
            
        Returns:
            List of dictionaries with sentence and bounding box information.
            Output format should strictly be:
            [{'sentence': str, 'bbox': {'x': %, 'y': %, 'width': %, 'height': %}}, ...]
            
            Where:
            - 'sentence': The original sentence that was searched for
            - 'bbox': Dictionary with percentage-based coordinates:
                - 'x': Left position as percentage of page width
                - 'y': Top position as percentage of page height  
                - 'width': Width as percentage of page width
                - 'height': Height as percentage of page height
            - If sentence not found, bbox should be empty dict: {}
        """
        # Ensure implementation returns the correct format
        raise NotImplementedError("Subclasses must implement highlight() method and return "
                                 "format: [{'sentence': str, 'bbox': {'x': %, 'y': %, 'width': %, 'height': %}}, ...]")