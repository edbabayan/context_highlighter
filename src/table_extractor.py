import json
from pathlib import Path
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions


def sort_tables_by_position(table_data):
    """
    Sort tables by page, then by height (top to bottom), then by left position.
    
    For BOTTOMLEFT coordinate system:
    - Higher 't' values = higher on page (top)
    - Lower 't' values = lower on page (bottom)
    
    Args:
        table_data: List of table dictionaries with bbox information
        
    Returns:
        Sorted list of tables
    """
    def sort_key(table):
        page = table['page']
        bbox = table['bbox']
        coord_origin = table['coord_origin']
        
        if coord_origin == 'BOTTOMLEFT':
            # For BOTTOMLEFT: higher 't' = higher on page, so we want descending order
            height_key = -bbox['t']  # Negative for descending sort (top to bottom)
        else:  # TOPLEFT
            # For TOPLEFT: lower 't' = higher on page, so we want ascending order
            height_key = bbox['t']
        
        left_key = bbox['l']  # Left to right (ascending)
        
        return page, height_key, left_key
    
    return sorted(table_data, key=sort_key)


def extract_tables_from_pdf(pdf_path: str, output_dir: Path):
    # Prepare options for table extraction
    pipeline_options = PdfPipelineOptions(do_table_structure=True)
    pipeline_options.table_structure_options.do_cell_matching = False

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    # Convert PDF to document model
    document = doc_converter.convert(pdf_path)

    # Collect table metadata
    table_data = [
        {
            "page": table.prov[0].page_no,
            "bbox": {
                "l": table.prov[0].bbox.l,
                "t": table.prov[0].bbox.t,
                "r": table.prov[0].bbox.r,
                "b": table.prov[0].bbox.b
            },
            "coord_origin": table.prov[0].bbox.coord_origin.value
        }
        for table in document.document.tables
    ]
    
    # Sort tables by page, then by height (top to bottom), then by left position
    sorted_table_data = sort_tables_by_position(table_data)

    with open(output_dir, "w") as f:
        json.dump(sorted_table_data, f, indent=4)

    print(f"Saved extracted tables metadata to {output_dir}")


if __name__ == '__main__':
    from src.config import CFG

    _pdf_path = "/Users/eduard_babayan/Documents/context_highlighter/Document.pdf"
    extract_tables_from_pdf(
        pdf_path=_pdf_path,
        output_dir=CFG.tables_dir
    )