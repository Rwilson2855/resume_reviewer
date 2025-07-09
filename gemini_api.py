import os
import google.generativeai as genai
from fpdf import FPDF

def review_and_improve_resume(path):
    # Configure Gemini API
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Feedback prompt (Gen Z style)
    feedback_prompt = (
        "This is a resume. Review it and give feedback in Gen Z slang. "
        "If it's bad, say 'bro you're cooked' and explain why. "
        "If it's good, say 'you're chillin'. Give specific improvement tips, all in Zoomer talk."
    )

    # Ethical improvement prompt
    improve_prompt = (
        "Rewrite this resume to make it as strong and impressive as possible, using only the information provided. "
        "Format the resume with clear section headings (such as Education, Experience, Skills, Projects). "
        "Use bullet points for achievements and responsibilities. "
        "Keep descriptions concise and impactful—avoid unnecessary verbosity. "
        "Limit the resume to a maximum of two pages. "
        "Use strong action verbs and quantify achievements when possible, but do not invent information. "
        "Do not add new experiences or skills not present in the original resume. "
        "Return only the improved resume, formatted as plain text suitable for conversion to PDF."
    )

    # Upload and process
    sample_doc = genai.upload_file(path=path, mime_type='application/pdf')
    feedback_response = model.generate_content([sample_doc, feedback_prompt])
    feedback = feedback_response.text

    improved_response = model.generate_content([sample_doc, improve_prompt])
    improved_resume_text = improved_response.text

    return feedback, improved_resume_text

def text_to_pdf(text, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Replace unsupported characters with '?'
    safe_text = text.encode('latin-1', 'replace').decode('latin-1')
    for line in safe_text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(output_path)

