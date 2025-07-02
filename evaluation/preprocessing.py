"""
Data Preprocessing Module for PDF Text Highlighting Evaluation.

This module handles the preprocessing of annotation data from LabelStudio or similar
annotation tools into a standardized format for evaluation. It converts raw annotation
JSON files into clean, structured data that can be used by the evaluation system.

Features:
- Clean and standardize annotation data from various sources
- Group annotations by page number for efficient processing
- Extract text and bounding box information
- Handle multiple annotation formats and edge cases
- Batch processing of multiple annotation files

Usage:
    # Process all annotation files
    process_all_json_files()
    
    # Process a single file
    cleaned_data = clean_json_file("annotations.json")
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from config import CFG


def clean_json_file(input_file_path: Path) -> List[Dict[str, Any]]:
    """Clean a single JSON file and organize results by page number."""
    with open(input_file_path, 'r') as f:
        data = json.load(f)
    
    pages = {}
    
    for item in data:
        # Extract page number from file_upload
        page_filename = None
        if 'file_upload' in item:
            file_upload = item['file_upload']
            
            # Handle both page_ and page-patterns
            if 'page_' in file_upload:
                page_part = file_upload.split('page_')[1]
            elif 'page-' in file_upload:
                page_part = file_upload.split('page-')[1]
            else:
                continue
            
            # Extract page number and extension
            page_num_with_ext = page_part.split('.', 1)  # Split only on first dot
            page_num = str(int(page_num_with_ext[0]))  # Remove leading zeros
            original_ext = page_num_with_ext[1] if len(page_num_with_ext) > 1 else 'png'
            page_filename = f"{page_num}.{original_ext}"
        
        if not page_filename:
            continue
            
        if page_filename not in pages:
            pages[page_filename] = {
                'file_name': page_filename,
                'results': []
            }
        
        if 'annotations' in item:
            for annotation in item['annotations']:
                if 'result' in annotation:
                    grouped_results = {}
                    
                    for result in annotation['result']:
                        if 'id' in result and 'value' in result:
                            result_id = result['id']
                            
                            if result_id not in grouped_results:
                                grouped_results[result_id] = {
                                    'bbox': None,
                                    'text': None,
                                    'original_width': result.get('original_width'),
                                    'original_height': result.get('original_height')
                                }
                            
                            if result['type'] == 'rectangle':
                                grouped_results[result_id]['bbox'] = {
                                    'x': result['value']['x'],
                                    'y': result['value']['y'], 
                                    'width': result['value']['width'],
                                    'height': result['value']['height']
                                }
                            
                            elif result['type'] == 'textarea' and 'text' in result['value']:
                                grouped_results[result_id]['text'] = result['value']['text'][0] if result['value']['text'] else ""
                    
                    for result_id, group_data in grouped_results.items():
                        if group_data['text'] and group_data['bbox']:
                            cleaned_entry = {
                                'text': group_data['text'],
                                'bbox': group_data['bbox'],
                                'original_width': group_data['original_width'],
                                'original_height': group_data['original_height']
                            }
                            pages[page_filename]['results'].append(cleaned_entry)
    
    return list(pages.values())


def process_all_json_files():
    """Process all JSON files from CFG.json_dir and save to CFG.processed_json_dir."""
    input_path = CFG.json_dir
    output_path = CFG.processed_json_dir
    output_path.mkdir(exist_ok=True, parents=True)
    
    json_files = list(input_path.glob('*.json'))
    
    for json_file in json_files:
        cleaned_data = clean_json_file(json_file)
        output_file = output_path / json_file.name  # Same filename
        
        with open(output_file, 'w') as f:
            json.dump(cleaned_data, f, indent=2)
        
        print(f"Processed: {json_file.name} -> {len(cleaned_data)} pages")
