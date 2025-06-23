import fitz  # PyMuPDF
import json

def get_table_info_for_page(tables_json_path, page_number):
    """
    Get information about all tables on a specific page, sorted by position.
    
    Args:
        tables_json_path: Path to the tables metadata JSON file
        page_number: Page number to get tables for
        
    Returns:
        List of table info with position details
    """
    with open(tables_json_path, 'r') as f:
        tables_data = json.load(f)
    
    page_tables = [table for table in tables_data if table['page'] == page_number]
    
    print(f"\n=== Tables on page {page_number} ===")
    for i, table in enumerate(page_tables):
        bbox = table['bbox']
        coord_origin = table['coord_origin']
        
        if coord_origin == 'BOTTOMLEFT':
            print(f"Table {i}: Top={bbox['t']:.1f}, Left={bbox['l']:.1f}, Right={bbox['r']:.1f}, Bottom={bbox['b']:.1f} ({coord_origin})")
        else:
            print(f"Table {i}: Top={bbox['t']:.1f}, Left={bbox['l']:.1f}, Right={bbox['r']:.1f}, Bottom={bbox['b']:.1f} ({coord_origin})")
    
    return page_tables

def highlight_phrase_in_table(pdf_path, output_path, page_number, phrase, table_index=0, tables_json_path="tables.json"):
    """
    Highlight a phrase within a specific table on a page.
    Tables are now indexed by position: top-to-bottom, then left-to-right.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the highlighted PDF
        page_number: Page number (0-indexed)
        phrase: Text phrase to highlight
        table_index: Index of the table on the page (0=top-left table, 1=next table, etc.)
        tables_json_path: Path to the tables metadata JSON file
    """
    print(f"\n=== Searching for '{phrase}' in table {table_index} on page {page_number} ===")
    
    # Load table metadata (now pre-sorted by position)
    with open(tables_json_path, 'r') as f:
        tables_data = json.load(f)
    
    # Find tables on the specified page (already sorted by position)
    page_tables = [table for table in tables_data if table['page'] == page_number]
    
    if not page_tables:
        print(f"No tables found on page {page_number}")
        return
    
    # Show all available tables on this page
    print(f"Found {len(page_tables)} table(s) on page {page_number}:")
    for i, table in enumerate(page_tables):
        bbox = table['bbox']
        coord_origin = table['coord_origin']
        print(f"  Table {i}: Top={bbox['t']:.1f}, Left={bbox['l']:.1f} ({coord_origin})")
    
    if table_index >= len(page_tables):
        print(f"Table index {table_index} not found on page {page_number}. Available indices: 0-{len(page_tables)-1}")
        return
    
    target_table = page_tables[table_index]
    table_bbox = target_table['bbox']
    print(f"Targeting table {table_index}: Top={table_bbox['t']:.1f}, Left={table_bbox['l']:.1f}")
    
    doc = fitz.open(pdf_path)
    page = doc[page_number-1]
    page_height = page.rect.height
    
    # Convert table bbox to PyMuPDF coordinates
    if target_table['coord_origin'] == 'BOTTOMLEFT':
        table_rect = fitz.Rect(
            table_bbox['l'], 
            page_height - table_bbox['t'],
            table_bbox['r'], 
            page_height - table_bbox['b']
        )
    else:  # TOPLEFT
        table_rect = fitz.Rect(
            table_bbox['l'], 
            table_bbox['t'],
            table_bbox['r'], 
            table_bbox['b']
        )
    
    # Search for phrase in the entire page
    text_instances = page.search_for(phrase)
    
    # Filter instances that fall within the table bounds
    table_instances = []
    for inst in text_instances:
        if table_rect.intersects(inst):
            table_instances.append(inst)
    
    if not table_instances:
        print(f"Phrase '{phrase}' not found in table {table_index} on page {page_number}")
        doc.close()
        return
    
    # Highlight the instances found in the table
    for inst in table_instances:
        highlight = page.add_highlight_annot(inst)
        highlight.update()
    
    doc.save(output_path)
    doc.close()
    print(f"Highlighted '{phrase}' in table {table_index} on page {page_number}, saved to {output_path}")

def highlight_phrase(pdf_path, output_path, page_number, phrase):
    doc = fitz.open(pdf_path)
    page = doc[page_number]
    
    text_instances = page.search_for(phrase)
    if not text_instances:
        print(f"Phrase '{phrase}' not found on page {page_number}")
        doc.close()
        return
    
    for inst in text_instances:
        highlight = page.add_highlight_annot(inst)
        highlight.update()
    
    doc.save(output_path)
    doc.close()
    print(f"Highlighted '{phrase}' on page {page_number}, saved to {output_path}")

def highlight_row(pdf_path, output_path, page_number, bbox_bl):
    doc = fitz.open(pdf_path)
    page = doc[page_number]
    page_h = page.rect.height

    l_bl, t_bl, r_bl, b_bl = bbox_bl
    if t_bl < b_bl:
        t_bl, b_bl = b_bl, t_bl

    y0 = page_h - t_bl
    y1 = page_h - b_bl
    x0 = l_bl
    x1 = r_bl

    quad = fitz.Quad(
        fitz.Point(x0, y0),
        fitz.Point(x1, y0),
        fitz.Point(x0, y1),
        fitz.Point(x1, y1)
    )

    annot = page.add_highlight_annot(quad)
    annot.update()
    doc.save(output_path)
    doc.close()
    print(f"Highlighted PDF saved to {output_path}")