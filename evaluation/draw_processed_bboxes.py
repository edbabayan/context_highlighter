import json
import fitz  # PyMuPDF
from pathlib import Path
from config import CFG


def draw_processed_bboxes(pdf_dir, ground_truth_bboxes, predicted_bboxes, function_name):
    """
    Draw bounding boxes on PDFs with ground truth in red and predicted in blue.
    
    Args:
        pdf_dir (str): Directory containing PDF files
        ground_truth_bboxes (dict): Ground truth bounding boxes data
        predicted_bboxes (dict): Predicted bounding boxes data
        function_name (str): Name of the function for output directory
    """
    # Create output directory
    output_dir = CFG.data_dir.joinpath(function_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all PDF files in the directory
    pdf_files = list(Path(pdf_dir).glob("*.pdf"))
    
    for pdf_file in pdf_files:
        pdf_name = pdf_file.stem
        
        # Check if we have data for this PDF
        if pdf_name not in ground_truth_bboxes and pdf_name not in predicted_bboxes:
            continue
            
        print(f"Processing PDF: {pdf_name}")
        
        # Open PDF
        pdf = fitz.open(str(pdf_file))
        
        # Process each page
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # Draw ground truth bboxes in red
            if pdf_name in ground_truth_bboxes:
                gt_data = ground_truth_bboxes[pdf_name]
                for page_data in gt_data:
                    if page_data.get('page_number', 1) - 1 == page_num:
                        for result in page_data.get('results', []):
                            bbox_data = result['bbox']
                            
                            # Convert percentage coordinates to PDF coordinates
                            x = (bbox_data['x'] / 100.0) * page_width
                            y = (bbox_data['y'] / 100.0) * page_height  
                            width = (bbox_data['width'] / 100.0) * page_width
                            height = (bbox_data['height'] / 100.0) * page_height
                            
                            # Create rectangle
                            rect = fitz.Rect(x, y, x + width, y + height)
                            
                            # Draw bounding box in red
                            page.draw_rect(rect, color=(1, 0, 0), width=2)
            
            # Draw predicted bboxes in blue
            if pdf_name in predicted_bboxes:
                pred_data = predicted_bboxes[pdf_name]
                for page_data in pred_data:
                    if page_data.get('page_number', 1) - 1 == page_num:
                        for result in page_data.get('results', []):
                            bbox_data = result['bbox']
                            
                            # Convert percentage coordinates to PDF coordinates
                            x = (bbox_data['x'] / 100.0) * page_width
                            y = (bbox_data['y'] / 100.0) * page_height  
                            width = (bbox_data['width'] / 100.0) * page_width
                            height = (bbox_data['height'] / 100.0) * page_height
                            
                            # Create rectangle
                            rect = fitz.Rect(x, y, x + width, y + height)
                            
                            # Draw bounding box in blue
                            page.draw_rect(rect, color=(0, 0, 1), width=2)
        
        # Save the result
        output_path = output_dir / f"{pdf_name}_highlighted.pdf"
        pdf.save(str(output_path))
        pdf.close()
        
        print(f"Saved highlighted PDF: {output_path}")


def draw_bboxes_from_processed_json():
    """
    Legacy function - Draw bounding boxes for the first page object from processed JSON file
    using the corresponding PDF.
    """
    # File paths
    processed_json_path = "../data/processed_json/02-15-2024-FR-(Final).json"
    pdf_path = "../data/pdfs/02-15-2024-FR-(Final).pdf"
    output_path = "../highlighted_processed_first_page.pdf"
    
    # Load processed JSON data
    with open(processed_json_path, 'r') as f:
        pages_data = json.load(f)
    
    if not pages_data:
        print("No pages found in processed JSON")
        return
    
    # Get the first page object
    first_page = pages_data[0]
    page_filename = first_page['file_name']
    results = first_page['results']
    
    print(f"Processing first page: {page_filename}")
    print(f"Number of text results: {len(results)}")
    
    # Extract page number from filename (e.g., "25.png" -> 25)
    page_number = int(page_filename.split('.')[0])
    
    # Open PDF
    pdf = fitz.open(pdf_path)
    
    # Check if page number is valid
    if page_number < 1 or page_number > len(pdf):
        print(f"Invalid page number {page_number}")
        pdf.close()
        return
    
    # Get the specific page (convert to 0-indexed)
    page = pdf[page_number - 1]
    
    # Get page dimensions
    page_rect = page.rect
    page_width = page_rect.width
    page_height = page_rect.height
    
    print(f"Page {page_number} dimensions: {page_width} x {page_height}")
    
    # Convert percentage coordinates to PDF coordinates and draw
    for result in results:
        text = result['text']
        bbox_data = result['bbox']
        
        # Convert percentage coordinates to PDF coordinates
        x = (bbox_data['x'] / 100.0) * page_width
        y = (bbox_data['y'] / 100.0) * page_height  
        width = (bbox_data['width'] / 100.0) * page_width
        height = (bbox_data['height'] / 100.0) * page_height
        
        # Create rectangle (left, top, right, bottom)
        rect = fitz.Rect(x, y, x + width, y + height)
        
        print(f"Text '{text}': bbox {rect}")
        
        # Draw bounding box in red
        page.draw_rect(rect, color=(1, 0, 0), width=2)
    
    # Save the result
    pdf.save(output_path)
    pdf.close()
    
    print(f"Bounding boxes drawn and saved to: {output_path}")
    print(f"Drew {len(results)} red bounding boxes")


if __name__ == "__main__":
    draw_bboxes_from_processed_json()