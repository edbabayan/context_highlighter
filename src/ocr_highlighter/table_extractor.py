import json
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageDraw
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from loguru import logger

from src.config import CFG


def extract_tables_from_pdf(pdf_path: str, output_dir: Path = None):
    logger.info(f"Starting table extraction from PDF: {pdf_path}")
    
    # Use CFG paths if not provided
    if output_dir is None:
        output_dir = CFG.tables_dir
    
    # Ensure temp directory exists
    CFG.temp_dir.mkdir(exist_ok=True)
    
    logger.debug("Preparing table extraction options")
    # Prepare options for table extraction
    pipeline_options = PdfPipelineOptions(do_table_structure=True)
    pipeline_options.table_structure_options.do_cell_matching = False

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    logger.info("Converting PDF to document model with docling")
    # Convert PDF to document model
    document = doc_converter.convert(pdf_path)
    logger.info(f"Found {len(document.document.tables)} tables in document")
    
    logger.debug("Opening PDF with PyMuPDF for coordinate conversion")
    # Open PDF with PyMuPDF to convert coordinates to actual pixels
    pdf_doc = fitz.open(pdf_path)
    page = pdf_doc[0]  # Single page PDF
    
    logger.debug("Creating pixmap for coordinate conversion")
    # Get pixel map to determine actual pixel dimensions
    pix = page.get_pixmap()
    pixels_per_point_x = pix.width / page.rect.width
    pixels_per_point_y = pix.height / page.rect.height
    logger.debug(f"Pixel conversion ratios: X={pixels_per_point_x:.2f}, Y={pixels_per_point_y:.2f}")
    
    logger.info("Converting table coordinates to pixels")
    # Collect table metadata with actual pixel coordinates
    table_data = []
    for i, table in enumerate(document.document.tables):
        logger.debug(f"Processing table {i+1}/{len(document.document.tables)}")
        orig_bbox = table.prov[0].bbox
        
        # Convert PDF points to actual pixels
        if orig_bbox.coord_origin.value == "BOTTOMLEFT":
            # Convert from bottom-left origin to top-left origin
            bbox_pixels = {
                "l": int(orig_bbox.l * pixels_per_point_x),
                "t": int((page.rect.height - orig_bbox.t) * pixels_per_point_y),  # Flip Y
                "r": int(orig_bbox.r * pixels_per_point_x),
                "b": int((page.rect.height - orig_bbox.b) * pixels_per_point_y)   # Flip Y
            }
        else:
            # Already top-left origin
            bbox_pixels = {
                "l": int(orig_bbox.l * pixels_per_point_x),
                "t": int(orig_bbox.t * pixels_per_point_y),
                "r": int(orig_bbox.r * pixels_per_point_x),
                "b": int(orig_bbox.b * pixels_per_point_y)
            }
        
        # Ensure top < bottom for drawing
        if bbox_pixels["t"] > bbox_pixels["b"]:
            bbox_pixels["t"], bbox_pixels["b"] = bbox_pixels["b"], bbox_pixels["t"]
        
        table_data.append({
            "page": table.prov[0].page_no,
            "bbox": bbox_pixels,
            "coord_origin": "TOPLEFT"  # Always use TOPLEFT after conversion
        })
        logger.debug(f"Table {i}: bbox={bbox_pixels}")
    
    logger.info("Creating visualization image with table bounding boxes")
    # Create image with table bounding boxes drawn
    img_data = pix.tobytes("png")
    image = Image.open(fitz.io.BytesIO(img_data))
    draw = ImageDraw.Draw(image)
    
    # Draw each table bounding box
    for i, table_info in enumerate(table_data):
        logger.debug(f"Drawing table {i} bounding box")
        bbox = table_info["bbox"]
        # Draw rectangle around table
        draw.rectangle(
            [bbox["l"], bbox["t"], bbox["r"], bbox["b"]], 
            outline="red", 
            width=3
        )
        # Add table index label
        draw.text(
            (bbox["l"] + 5, bbox["t"] + 5), 
            f"Table {i}", 
            fill="red"
        )
    
    # Save image with table boxes
    image.save(CFG.table_images_dir)
    logger.info(f"Saved table visualization to {CFG.table_images_dir}")
    
    pdf_doc.close()

    logger.debug("Sorting tables by position (top to bottom, left to right)")
    # Sort tables: top to bottom, then left to right for same height
    table_data.sort(key=lambda t: (t["bbox"]["t"], t["bbox"]["l"]))

    logger.info(f"Saving table metadata to {output_dir}")
    with open(output_dir, "w") as f:
        json.dump(table_data, f, indent=4)

    logger.success(f"Table extraction completed. Found {len(table_data)} tables. Metadata saved to {output_dir}")
    return table_data


if __name__ == '__main__':
    logger.info("Running table extraction as main module")
    
    _pdf_path = CFG.temp_pdf_path
    logger.info(f"Processing PDF: {_pdf_path}")

    if not _pdf_path.exists():
        logger.error(f"PDF file not found: {_pdf_path}")
    else:
        extract_tables_from_pdf(pdf_path=str(_pdf_path))