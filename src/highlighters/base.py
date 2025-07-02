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
            List of dictionaries with sentence and bounding box information
            Format: [{'sentence': str, 'bbox': {'x': %, 'y': %, 'width': %, 'height': %}}, ...]
        """
        pass