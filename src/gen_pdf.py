from weasyprint import HTML
import sys
import os

def generate_pdf(html_input_path, output_pdf_path):
    """
    Convert an HTML resume to a styled PDF using WeasyPrint.

    Args:
        html_input_path (str): Path to the input HTML file (must have linked CSS).
        output_pdf_path (str): Path for the output PDF file.
    """
    if not os.path.exists(html_input_path):
        print(f"Error: HTML input file does not exist: {html_input_path}")
        return

    try:
        print(f"Generating PDF from {html_input_path} ...")
        # Use base_url='.' if CSS or relative assets need to be resolved within current folder
        HTML(html_input_path, base_url='.').write_pdf(output_pdf_path)
        print(f"PDF successfully saved to {output_pdf_path}")
    except Exception as e:
        print(f"Error during PDF generation: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gen_pdf.py <input_resume.html> <output_resume.pdf>")
    else:
        html_path = sys.argv[1]
        pdf_path = sys.argv[2]
        generate_pdf(html_path, pdf_path)
