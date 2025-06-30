import json
import os
from pathlib import Path
from typing import List, Dict, Tuple, Callable
import numpy as np
from config import CFG


def calculate_iou(box1: List[float], box2: List[float]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.
    
    Args:
        box1, box2: [left, top, right, bottom] format
        
    Returns:
        IoU score between 0 and 1
    """
    # Calculate intersection coordinates
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    # Calculate intersection area
    if x2 <= x1 or y2 <= y1:
        return 0.0
    
    intersection = (x2 - x1) * (y2 - y1)
    
    # Calculate union area
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0


def convert_percentage_to_absolute(bbox_percent: Dict, page_width: float, page_height: float) -> List[float]:
    """
    Convert percentage-based bounding box to absolute coordinates.
    
    Args:
        bbox_percent: {'x': %, 'y': %, 'width': %, 'height': %}
        page_width, page_height: PDF page dimensions
        
    Returns:
        [left, top, right, bottom] in absolute coordinates
    """
    left = (bbox_percent['x'] / 100.0) * page_width
    top = (bbox_percent['y'] / 100.0) * page_height
    width = (bbox_percent['width'] / 100.0) * page_width
    height = (bbox_percent['height'] / 100.0) * page_height
    
    return [left, top, left + width, top + height]


def calculate_ap_for_page(predicted_boxes: List[Dict], ground_truth_boxes: List[Dict], 
                         page_width: float, page_height: float, iou_threshold: float = 0.5) -> float:
    """
    Calculate Average Precision for a single page.
    
    Args:
        predicted_boxes: List of predicted boxes with 'sentence' and 'bbox' keys
        ground_truth_boxes: List of ground truth boxes with 'text' and 'bbox' keys
        page_width, page_height: PDF page dimensions
        iou_threshold: IoU threshold for positive detection
        
    Returns:
        Average Precision score
    """
    if not ground_truth_boxes:
        return 1.0 if not predicted_boxes else 0.0
    
    if not predicted_boxes:
        return 0.0
    
    # Convert all boxes to absolute coordinates
    pred_abs = []
    for pred in predicted_boxes:
        if isinstance(pred['bbox'], list) and len(pred['bbox']) == 4:
            # Already in absolute coordinates [left, top, right, bottom]
            pred_abs.append({
                'sentence': pred['sentence'],
                'bbox': pred['bbox'],
                'confidence': pred.get('confidence', 1.0)
            })
        else:
            # Convert from percentage
            abs_bbox = convert_percentage_to_absolute(pred['bbox'], page_width, page_height)
            pred_abs.append({
                'sentence': pred['sentence'],
                'bbox': abs_bbox,
                'confidence': pred.get('confidence', 1.0)
            })

    gt_abs = []
    for gt in ground_truth_boxes:
        abs_bbox = convert_percentage_to_absolute(gt['bbox'], page_width, page_height)
        gt_abs.append({
            'text': gt['text'],
            'bbox': abs_bbox
        })
    
    # Sort predictions by confidence (descending)
    pred_abs.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Track which ground truth boxes have been matched
    gt_matched = [False] * len(gt_abs)
    
    # Calculate precision and recall at each prediction
    true_positives = []
    false_positives = []
    
    for pred in pred_abs:
        best_iou = 0.0
        best_gt_idx = -1
        
        # Find best matching ground truth box
        for gt_idx, gt in enumerate(gt_abs):
            if gt_matched[gt_idx]:
                continue
                
            iou = calculate_iou(pred['bbox'], gt['bbox'])
            if iou > best_iou:
                best_iou = iou
                best_gt_idx = gt_idx
        
        # Check if it's a true positive
        if best_iou >= iou_threshold and best_gt_idx != -1:
            true_positives.append(1)
            false_positives.append(0)
            gt_matched[best_gt_idx] = True
        else:
            true_positives.append(0)
            false_positives.append(1)
    
    # Calculate precision and recall arrays
    tp_cumsum = np.cumsum(true_positives)
    fp_cumsum = np.cumsum(false_positives)
    
    precisions = tp_cumsum / (tp_cumsum + fp_cumsum)
    recalls = tp_cumsum / len(gt_abs)
    
    # Calculate Average Precision using 11-point interpolation
    ap = 0.0
    for t in np.arange(0.0, 1.1, 0.1):
        if np.sum(recalls >= t) == 0:
            p = 0
        else:
            p = np.max(precisions[recalls >= t])
        ap += p / 11.0
    
    return ap


def evaluate_highlighting_function(highlighting_func: Callable, pdfs_dir: str, processed_json_dir: str) -> Dict:
    """
    Evaluate a highlighting function using mean Average Precision at IoU 0.75.
    
    Args:
        highlighting_func: Function that takes (pdf_path, page_num, sentences) and returns bounding boxes
        pdfs_dir: Directory containing PDF files
        processed_json_dir: Directory containing processed JSON annotation files
        
    Returns:
        Dictionary with evaluation metrics
    """
    pdfs_path = Path(pdfs_dir)
    json_path = Path(processed_json_dir)
    
    total_ap = 0.0
    total_pages = 0
    file_results = {}
    
    # Process each JSON file
    json_files = list(json_path.glob('*.json'))
    
    for json_file in json_files:
        # Find corresponding PDF file
        pdf_name = json_file.stem + '.pdf'
        pdf_file = pdfs_path / pdf_name
        
        if not pdf_file.exists():
            print(f"Warning: PDF file not found for {json_file.name}")
            continue
        
        # Load ground truth annotations
        with open(json_file, 'r') as f:
            pages_data = json.load(f)
        
        file_ap_scores = []
        
        for page_data in pages_data:
            page_filename = page_data['file_name']
            page_number = int(page_filename.split('.')[0])
            gt_results = page_data['results']
            
            if not gt_results:  # Skip pages with no annotations
                continue
            
            # Extract sentences for prediction
            sentences = [result['text'] for result in gt_results]
            
            # Get page dimensions from ground truth
            if gt_results:
                page_width = gt_results[0]['original_width']
                page_height = gt_results[0]['original_height']
            else:
                continue
            
            try:
                # Call highlighting function to get predictions
                predicted_boxes = highlighting_func(pdf_file, page_number, sentences)
                
                # Calculate AP for this page
                ap = calculate_ap_for_page(predicted_boxes, gt_results, page_width, page_height)
                
                file_ap_scores.append(ap)
                total_ap += ap
                total_pages += 1
                
                print(f"Page {page_number} of {json_file.name}: AP = {ap:.3f}")
                
            except Exception as e:
                print(f"Error processing page {page_number} of {json_file.name}: {e}")
                continue
        
        if file_ap_scores:
            file_map = np.mean(file_ap_scores)
            file_results[json_file.name] = {
                'mAP': file_map,
                'num_pages': len(file_ap_scores),
                'ap_scores': file_ap_scores
            }
            print(f"File {json_file.name}: mAP = {file_map:.3f} ({len(file_ap_scores)} pages)")
    
    # Calculate overall mAP
    overall_map = total_ap / total_pages if total_pages > 0 else 0.0
    
    results = {
        'overall_mAP_75': overall_map,
        'total_pages_evaluated': total_pages,
        'file_results': file_results
    }
    
    return results


def example_highlighting_function(pdf_path: str, page_number: int, sentences: List[str]) -> List[Dict]:
    """
    Example highlighting function that uses the OCR highlighter.
    Replace this with your actual highlighting function.
    
    Args:
        pdf_path: Path to PDF file
        page_number: Page number to process
        sentences: List of sentences to find
        
    Returns:
        List of dictionaries with 'sentence' and 'bbox' keys
    """
    # Import your highlighting function here
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from src.ocr_highlighter.ocr_highlighter import highlight_sentences_with_ocr
    
    # Create a temporary output file (we only need the bboxes)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_output = tmp_file.name
    
    try:
        # Call the highlighting function
        results = highlight_sentences_with_ocr(
            pdf_path, tmp_output, page_number, sentences, table=True, table_index=0
        )
        
        # Convert results to expected format
        predicted_boxes = []
        for result in results:
            predicted_boxes.append({
                'sentence': result['sentence'],
                'bbox': result['bbox'],  # Should be [left, top, right, bottom]
                'confidence': 1.0
            })
        
        return predicted_boxes
        
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_output):
            os.unlink(tmp_output)


if __name__ == "__main__":
    from src.pymupdf_highlighter.row_highlighter import highlight_sentences_on_page

    # Example usage
    pdfs_dir = CFG.pdf_dir
    processed_json_dir = CFG.processed_json_dir
    
    print("Starting evaluation...")
    print(f"PDFs directory: {pdfs_dir}")
    print(f"Processed JSON directory: {processed_json_dir}")
    
    # Run evaluation
    results = evaluate_highlighting_function(
        highlight_sentences_on_page,
        str(pdfs_dir),
        str(processed_json_dir)
    )
    
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Overall mAP@0.75: {results['overall_mAP_75']:.3f}")
    print(f"Total pages evaluated: {results['total_pages_evaluated']}")
    
    print("\nPer-file results:")
    for filename, file_result in results['file_results'].items():
        print(f"  {filename}: mAP = {file_result['mAP']:.3f} ({file_result['num_pages']} pages)")