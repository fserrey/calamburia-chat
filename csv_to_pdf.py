import csv
import os
from fpdf import FPDF

def csv_to_pdf(csv_file, pdf_file):
    """
    Reads a CSV with columns:
      couple_title, couple_link, couple_text_info
    and creates a PDF with the format:

    _________________________
    Pareja: <couple_title>
    Información de la pareja:
    <couple_text_info>
    _________________________

    for each row in the CSV.
    """

    # 1) Prepare the PDF object
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 2) Embed a TrueType font that supports Spanish & Unicode characters
    #    Make sure "DejaVuSans.ttf" is in the same folder or provide a full path
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", "", 12)

    # 3) Read rows from the CSV
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            couple_title = row.get("couple_title", "").strip()
            couple_text = row.get("couple_text_info", "").strip()
            # (If you want the link as well, you can retrieve row["couple_link"] here.)

            # 4) Write the structured content in the PDF
            pdf.multi_cell(0, 8, "_________________________")
            pdf.ln(3)
            pdf.multi_cell(0, 8, f"Pareja: {couple_title}")
            pdf.ln(4)
            pdf.multi_cell(0, 8, "Información de la pareja:")
            pdf.ln(4)

            # Because couple_text might be multiple paragraphs, split by lines
            for line in couple_text.split("\n"):
                pdf.multi_cell(0, 8, line)
            pdf.ln(4)

            pdf.multi_cell(0, 8, "_________________________")
            pdf.ln(10)

    # 5) Output the PDF
    pdf.output(pdf_file)
    print(f"PDF generated: {pdf_file}")

if __name__ == "__main__":
    # Example usage:
    input_csv = "calamburia_couples.csv"     # Where your CSV file is located
    output_pdf = "calamburia_couples.pdf"    # Desired PDF file name
    csv_to_pdf(input_csv, output_pdf)
