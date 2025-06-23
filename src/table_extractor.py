import os
import json
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions


def extract_tables_from_pdf(pdf_path: str, output_dir: str, output_filename: str = "tables.json"):
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

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save to JSON file
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w") as f:
        json.dump(table_data, f, indent=4)

    print(f"Saved extracted tables metadata to {output_path}")

if __name__ == '__main__':
    from src.config import CFG

    _pdf_path = "/Users/eduard_babayan/Documents/context_highlighter/Document.pdf"
    extract_tables_from_pdf(
        pdf_path=_pdf_path,
        output_dir=CFG.tables_dir
    )