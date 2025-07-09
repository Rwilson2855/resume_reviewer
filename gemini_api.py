import os
import google.generativeai as genai

def review_and_improve_resume(path):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    feedback_prompt = (
        "This is a resume. Review it and give feedback in Gen Z slang. "
        "If it's bad, say 'bro you're cooked' and explain why. "
        "If it's good, say 'you're chillin'. Give specific improvement tips, all in Zoomer talk."
    )

    improve_prompt = (
        "Rewrite this resume to be strong, concise, and well-formatted, using only the information provided. "
        "Format the resume using Markdown with clear section headings (## Education, ## Experience, ## Skills, etc.), "
        "and use bullet points for achievements and responsibilities. "
        "Keep it to one page, and do not add new experiences or skills. "
        "Return only the improved resume in Markdown format."
    )

    sample_doc = genai.upload_file(path=path, mime_type='application/pdf')
    feedback_response = model.generate_content([sample_doc, feedback_prompt])
    feedback = feedback_response.text

    improved_response = model.generate_content([sample_doc, improve_prompt])
    improved_resume_md = improved_response.text

    return feedback, improved_resume_md


from fpdf import FPDF

def markdown_to_pdf(md_text, output_path):
    from fpdf import FPDF
    try:
        pdf = FPDF(format='A4')
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        # ... rest of your PDF logic ...
        pdf.output(output_path)
        print(f"[PDF] Successfully wrote PDF to {output_path}")
    except Exception as e:
        print(f"[PDF] ERROR: {e}")
        import traceback
        traceback.print_exc()
