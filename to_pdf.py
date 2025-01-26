import re
from fpdf import FPDF
import os

def parse_tales_from_file(filename):
    """
    Reads the calamburia_ordered_tales.txt file,
    splits it into separate tales, and returns a list of:
      [ { "title": "...", "text": "..." }, ... ]
    """
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # Each tale is separated by a line of 60 '=' characters,
    # which in the scraper was: f.write("\n\n" + "="*60 + "\n\n")
    # We can split on that delimiter:
    raw_tales = content.split("\n" + "=" * 60 + "\n")

    tales_list = []
    for chunk in raw_tales:
        # Remove leading/trailing whitespace
        chunk = chunk.strip()
        if not chunk:
            # If there's an empty chunk (e.g., at the end), skip it
            continue
        
        # Split the chunk into lines
        lines = chunk.splitlines()
        
        # The first line contains the title, for example: "1 - 01. LA HISTORIA"
        # The rest are the paragraphs of the tale text.
        if len(lines) < 2:
            # If there's no text, skip
            continue
        
        title_line = lines[0].strip()
        tale_text = "\n".join(lines[1:])  # The rest is the story

        tales_list.append({
            "title": title_line,
            "text": tale_text
        })

    return tales_list

def create_pdf_from_tales(tales):
    """
    Given a list of tales (each is a dict with "title" and "text"),
    create a PDF called 'calamburia_tales.pdf' with them in order.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)

    pdf.set_font("DejaVu", "", 12)


    for tale in tales:
        # Print the title (e.g. "1 - 01. LA HISTORIA")
        pdf.multi_cell(0, 10, tale["title"])
        pdf.ln(5)

        # Print the paragraphs of the tale’s text
        for line in tale["text"].split("\n"):
            clean_line = line.replace("…", "...").replace("—", "-")
            pdf.multi_cell(0, 10, clean_line)
        pdf.ln(10)

    pdf.output("calamburia_couples.pdf")
    print("Saved all tales to 'calamburia_couples.pdf'.")

if __name__ == "__main__":
    # 1. Parse the tales from the text file
    tales = parse_tales_from_file("../../FSR/calamburia-chat/calamburia_couples.txt")
    
    # 2. Create the PDF from that list of tales
    create_pdf_from_tales(tales)
