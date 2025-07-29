import os
import sys
import google.generativeai as genai
from weasyprint import HTML

def review_and_improve_resume(input_pdf, css_path, html_path, output_pdf):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Prompt for improved resume as HTML
    improve_prompt = (
        "Rewrite this resume to be strong, concise, and well-formatted, using only the information provided. "
        "Format the resume as clean, professional HTML with clear section headings (<h2>), "
        "proper use of <ul> for achievements and responsibilities, and structure it to work well with my existing CSS. "
        "Do not add any new information. Return only the improved resume in HTML markup."
    )

    # Upload PDF, get improved HTML from Gemini
    uploaded_doc = genai.upload_file(path=input_pdf, mime_type="application/pdf")
    improved_response = model.generate_content([uploaded_doc, improve_prompt])
    improved_html = improved_response.text

    # Save improved HTML for reference (optional)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(improved_html)

    # Generate improved PDF with WeasyPrint using provided CSS
    HTML(string=improved_html, base_url=".").write_pdf(output_pdf, stylesheets=[css_path])

if __name__ == "__main__":
    # Paths can be user input or hardcoded, depending on app setup
    input_pdf = "resume.pdf"
    css_path = "static/resume.css"
    html_path = "templates/resume.html"
    output_pdf = "improved_resume.pdf"

    # Check API key
    if "GEMINI_API_KEY" not in os.environ:
        print("GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    review_and_improve_resume(input_pdf, css_path, html_path, output_pdf)
    print(f"Improved resume PDF generated: {output_pdf}")
