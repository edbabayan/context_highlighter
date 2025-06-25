import fitz  # PyMuPDF


def highlight_sentences_on_page(pdf_path, output_path, page_number, sentences):
    """
    Highlight multiple sentences on a specific page using simple search and highlight.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the highlighted PDF
        page_number: Page number (1-indexed)
        sentences: List of sentences to highlight
    """
    pdf = fitz.open(pdf_path)
    
    if page_number < 1 or page_number > len(pdf):
        print(f"Invalid page number {page_number}")
        pdf.close()
        return
    
    page = pdf[page_number - 1]
    
    for sentence in sentences:
        quads = page.search_for(sentence)
        if quads:
            page.add_highlight_annot(quads)
    
    pdf.save(output_path)
    pdf.close()
    print(f"Highlighted {len(sentences)} sentences on page {page_number}, saved to {output_path}")

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