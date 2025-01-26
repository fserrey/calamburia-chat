import csv
import os
from fpdf import FPDF


class PDFWithTOC(FPDF):
    """
    Extends FPDF to add a Table of Contents at the end (no page reordering).
    We'll keep track of each 'chapter' (couple) with its page number, then
    print a TOC on a new page at the conclusion.
    """

    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.alias_nb_pages()
        self.toc_entries = []  # Will hold dicts: { 'title': ..., 'page': ... }

        # Paths to your TTF font files (make sure they exist!)
        self.font_path_regular = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
        self.font_path_bold = os.path.join(os.path.dirname(__file__), "DejaVuSans-Bold.ttf")

        # Register both the regular and bold styles under the same "DejaVu" family.
        self.add_font("DejaVu", "", self.font_path_regular, uni=True)  # Regular style
        self.add_font("DejaVu", "B", self.font_path_bold, uni=True)    # Bold style

        self._width = self.w - 2 * self.l_margin  # for reference

    def header(self):
        """Optional: Override the header if you want a header on every page."""
        pass  # We'll keep it minimal for clarity.

    def footer(self):
        """Show page numbers in the footer."""
        self.set_y(-15)
        # Use the regular style for the footer
        self.set_font("DejaVu", "", 10)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")

    def add_title_page(self, doc_title="Parejas Calamburia"):
        """If you want a standalone cover page (optional)."""
        self.add_page()
        self.set_font("DejaVu", "B", 18)
        self.cell(0, 20, doc_title, ln=1, align="C")
        self.ln(10)

    def add_couple_page(self, title, text):
        """
        Inserts a new page for each couple:
          - Big heading for the 'Pareja' name
          - Subheading for the 'Información de la pareja'
          - Body text (1.5 line spacing)
        We'll store the page in the TOC as well.
        """
        self.add_page()
        # Record in the TOC with the current page number
        self.toc_entries.append({"title": title, "page": self.page_no()})

        # Heading (16-18pt, bold)
        self.set_font("DejaVu", "B", 18)
        self.multi_cell(0, 10, title)  # 10 is the cell height
        self.ln(5)

        # Subheading (14pt, bold)
        self.set_font("DejaVu", "B", 14)
        self.multi_cell(0, 8, "Información de la pareja")
        self.ln(5)

        # Body text (12pt, normal) with ~1.5 line spacing
        self.set_font("DejaVu", "", 12)
        line_height = 8 * 1.5  # ~1.5 spacing
        for line in text.split("\n"):
            self.multi_cell(0, line_height, line)
        self.ln(5)

    def insert_toc(self, toc_title="Índice / Table of Contents"):
        """
        Insert a Table of Contents page(s) **after** all couples (no page reordering).
        """
        # Create a fresh page for the TOC
        self.add_page()

        # Title for the TOC
        self.set_font("DejaVu", "B", 18)
        self.multi_cell(0, 10, toc_title, align="C")
        self.ln(10)

        # Sort entries alphabetically by 'title' (or by categories if you prefer).
        self.toc_entries.sort(key=lambda x: x["title"].lower())

        # Print the TOC items
        self.set_font("DejaVu", "", 12)
        for entry in self.toc_entries:
            title = entry["title"]
            page_number = entry["page"]
            # e.g. "• <title> ........................ page x"
            dotted_line = "." * (60 - len(title))
            line_str = f"• {title} {dotted_line} {page_number}"
            self.multi_cell(0, 8, line_str)


def csv_to_structured_pdf(csv_file, pdf_file):
    # Create the PDF object
    pdf = PDFWithTOC()
    pdf.set_auto_page_break(auto=True, margin=15)

    # (Optional) Add a title page
    # pdf.add_title_page("Calamburia: Equipos / Pairs")

    # Read CSV
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        couples = list(reader)  # read them all

    for row in couples:
        title = row.get("couple_title", "").strip()
        text_info = row.get("couple_text_info", "").strip()
        pdf.add_couple_page(title=title, text=text_info)

    # Insert the Table of Contents (which will appear at the end)
    pdf.insert_toc(toc_title="Índice / Table of Contents")

    # Output
    pdf.output(pdf_file)
    print(f"PDF generated: {pdf_file}")


if __name__ == "__main__":
    input_csv = "calamburia_couples.csv"  # your CSV file name
    output_pdf = "calamburia_couples.pdf"  # desired PDF file
    csv_to_structured_pdf(input_csv, output_pdf)
