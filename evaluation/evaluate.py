import json
from pathlib import Path
from typing import List, Dict, Callable

import numpy as np
import pandas as pd

from config import CFG
from draw_processed_bboxes import draw_processed_bboxes


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
        page_width: PDF page width
        page_height: PDF page height
        
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
        page_width: PDF page width
        page_height: PDF page height
        iou_threshold: IoU threshold for positive detection
        
    Returns:
        Average Precision score
    """
    if not ground_truth_boxes:
        return 1.0 if not predicted_boxes else 0.0
    
    # If no predictions, return 0.0 (all ground truths are false negatives)
    if not predicted_boxes:
        return 0.0
    
    # Convert all boxes to absolute coordinates and filter invalid ones
    pred_abs = []
    invalid_predictions = 0
    
    for pred in predicted_boxes:
        # Check for empty or invalid bounding boxes
        if not pred.get('bbox') or pred['bbox'] == {}:
            invalid_predictions += 1
            continue
            
        if isinstance(pred['bbox'], list) and len(pred['bbox']) == 4:
            # Already in absolute coordinates [left, top, right, bottom]
            pred_abs.append({
                'sentence': pred['sentence'],
                'bbox': pred['bbox'],
                'confidence': pred.get('confidence', 1.0)
            })
        elif isinstance(pred['bbox'], dict):
            # Check if bbox dict has required keys for percentage conversion
            required_keys = ['x', 'y', 'width', 'height']
            if all(key in pred['bbox'] for key in required_keys):
                # Convert from percentage
                abs_bbox = convert_percentage_to_absolute(pred['bbox'], page_width, page_height)
                pred_abs.append({
                    'sentence': pred['sentence'],
                    'bbox': abs_bbox,
                    'confidence': pred.get('confidence', 1.0)
                })
            else:
                invalid_predictions += 1
                continue
        else:
            invalid_predictions += 1
            continue

    # If all predictions were invalid, return 0.0 (all ground truths are false negatives)
    if not pred_abs:
        return 0.0

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


def evaluate_highlighting_function(highlighting_func: Callable, pdfs_dir: Path, processed_json_dir: Path) -> Dict:
    """
    Evaluate a highlighting function using mean Average Precision at IoU 0.75.
    
    Args:
        highlighting_func: Function that takes (pdf_path, page_num, sentences) and returns bounding boxes
        pdfs_dir: Directory containing PDF files
        processed_json_dir: Directory containing processed JSON annotation files
        
    Returns:
        Dictionary with evaluation metrics
    """
    pdfs_path = pdfs_dir
    json_path = processed_json_dir
    
    total_ap = 0.0
    total_pages = 0
    file_results = {}
    
    # Data structures for drawing bboxes
    ground_truth_bboxes = {}
    predicted_bboxes = {}
    
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
        file_page_numbers = []
        
        # Initialize data structures for this PDF
        pdf_stem = json_file.stem
        ground_truth_bboxes[pdf_stem] = []
        predicted_bboxes[pdf_stem] = []
        
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
                
                # Store ground truth bboxes for drawing
                ground_truth_bboxes[pdf_stem].append({
                    'page_number': page_number,
                    'results': gt_results
                })
                
                # Store predicted bboxes for drawing (convert to same format as ground truth)
                pred_results = []
                for pred in predicted_boxes:
                    if pred.get('bbox'):
                        # Convert absolute coordinates back to percentage if needed
                        if isinstance(pred['bbox'], list) and len(pred['bbox']) == 4:
                            # Convert from absolute [left, top, right, bottom] to percentage format
                            left, top, right, bottom = pred['bbox']
                            pred_results.append({
                                'text': pred.get('sentence', ''),
                                'bbox': {
                                    'x': (left / page_width) * 100,
                                    'y': (top / page_height) * 100,
                                    'width': ((right - left) / page_width) * 100,
                                    'height': ((bottom - top) / page_height) * 100
                                }
                            })
                        elif isinstance(pred['bbox'], dict):
                            # Already in percentage format
                            pred_results.append({
                                'text': pred.get('sentence', ''),
                                'bbox': pred['bbox']
                            })
                
                predicted_bboxes[pdf_stem].append({
                    'page_number': page_number,
                    'results': pred_results
                })
                
                # Calculate AP for this page
                ap = calculate_ap_for_page(predicted_boxes, gt_results, page_width, page_height)
                
                file_ap_scores.append(ap)
                file_page_numbers.append(page_number)
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
                'ap_scores': file_ap_scores,
                'page_numbers': file_page_numbers
            }
            print(f"File {json_file.name}: mAP = {file_map:.3f} ({len(file_ap_scores)} pages)")
    
    # Calculate overall mAP
    overall_map = total_ap / total_pages if total_pages > 0 else 0.0
    
    # Draw bounding boxes on PDFs
    function_name = highlighting_func.__name__
    print(f"\nDrawing bounding boxes for function: {function_name}")
    draw_processed_bboxes(str(pdfs_path), ground_truth_bboxes, predicted_bboxes, function_name)
    print(f"Highlighted PDFs saved in {CFG.data_dir.joinpath(function_name)}/")
    
    results = {
        'overall_mAP_75': overall_map,
        'total_pages_evaluated': total_pages,
        'file_results': file_results
    }
    
    return results


def save_results_to_excel(results: Dict, function_name: str, output_dir: str = None) -> str:
    """
    Save evaluation results to an Excel file with multiple sheets.
    
    Args:
        results: Dictionary with evaluation results from evaluate_highlighting_function
        function_name: Name of the highlighting function being evaluated
        output_dir: Output directory (defaults to data directory)
        
    Returns:
        Path to the saved Excel file
    """
    if output_dir is None:
        output_dir = CFG.data_dir
    else:
        output_dir = Path(output_dir)
    
    # Create Excel filename
    excel_filename = f"{function_name}.xlsx"
    excel_path = output_dir / excel_filename
    
    # Create Excel writer
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        
        # Create Summary Sheet
        summary_data = []
        for filename, file_result in results['file_results'].items():
            summary_data.append({
                'PDF_Name': filename.replace('.json', '.pdf'),
                'mAP_Score': file_result['mAP'],
                'Pages_Evaluated': file_result['num_pages']
            })
        
        # Add overall statistics
        summary_data.append({
            'PDF_Name': 'OVERALL_MEAN',
            'mAP_Score': results['overall_mAP_75'],
            'Pages_Evaluated': results['total_pages_evaluated']
        })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Create individual sheets for each PDF
        for filename, file_result in results['file_results'].items():
            pdf_name = filename.replace('.json', '')
            
            # Create page-level data using actual page numbers
            page_data = []
            for page_number, ap_score in zip(file_result['page_numbers'], file_result['ap_scores']):
                page_data.append({
                    'Page_Number': page_number,
                    'AP_Score': ap_score
                })
            
            # Add summary row
            page_data.append({
                'Page_Number': 'AVERAGE',
                'AP_Score': file_result['mAP']
            })
            
            page_df = pd.DataFrame(page_data)
            
            # Clean sheet name (Excel sheet names can't be too long or contain certain characters)
            sheet_name = pdf_name[:31].replace('/', '_').replace('\\', '_').replace('*', '_').replace('?', '_').replace(':', '_').replace('[', '_').replace(']', '_')
            
            page_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return str(excel_path)


if __name__ == "__main__":
    from src.pymupdf_highlighter.row_highlighter import highlight_sentences_on_page
    # from src.ocr_highlighter.ocr_highlighter import highlight_sentences_with_ocr

    # Example usage
    _pdfs_dir = CFG.pdf_dir
    _processed_json_dir = CFG.processed_json_dir
    
    print("Starting evaluation...")
    print(f"PDFs directory: {_pdfs_dir}")
    print(f"Processed JSON directory: {_processed_json_dir}")
    
    # Run evaluation
    _results = evaluate_highlighting_function(
        highlight_sentences_on_page,
        _pdfs_dir,
        _processed_json_dir
    )
    
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Overall mAP@0.75: {_results['overall_mAP_75']:.3f}")
    print(f"Total pages evaluated: {_results['total_pages_evaluated']}")
    
    print("\nPer-file results:")
    for _filename, _file_result in _results['file_results'].items():
        print(f"  {_filename}: mAP = {_file_result['mAP']:.3f} ({_file_result['num_pages']} pages)")
    
    # Save results to Excel
    _function_name = highlight_sentences_on_page.__name__
    _excel_path = save_results_to_excel(_results, _function_name)
    print(f"\nResults saved to Excel file: {_excel_path}")
