import os
import uuid
import traceback
import re
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from gemini_api import review_and_improve_resume

from fpdf import FPDF
from fpdf.enums import XPos, YPos

load_dotenv()
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def render_markdown_line(pdf, line, normal_font_size=12):
    bold_pattern = r'\*\*(.+?)\*\*'
    italic_pattern = r'\*(.+?)\*'
    pos = 0
    while pos < len(line):
        bold_match = re.search(bold_pattern, line[pos:])
        italic_match = re.search(italic_pattern, line[pos:])
        if bold_match and (not italic_match or bold_match.start() < italic_match.start()):
            if bold_match.start() > 0:
                pdf.set_font('DejaVu', '', normal_font_size)
                pdf.write(8, line[pos:pos+bold_match.start()])
            pdf.set_font('DejaVu', 'B', normal_font_size)
            pdf.write(8, bold_match.group(1))
            pos += bold_match.end()
        elif italic_match:
            if italic_match.start() > 0:
                pdf.set_font('DejaVu', '', normal_font_size)
                pdf.write(8, line[pos:pos+italic_match.start()])
            pdf.set_font('DejaVu', 'I', normal_font_size)
            pdf.write(8, italic_match.group(1))
            pos += italic_match.end()
        else:
            pdf.set_font('DejaVu', '', normal_font_size)
            pdf.write(8, line[pos:])
            break
    pdf.ln(8)

def markdown_to_pdf(md_text, output_path):
    pdf = FPDF(format='A4')
    pdf.add_page()
    font_path = os.path.join(BASE_DIR, "DejaVuSans.ttf")
    pdf.add_font('DejaVu', '', font_path)
    pdf.add_font('DejaVu', 'B', font_path)
    pdf.add_font('DejaVu', 'I', font_path)

    line_height = 8
    section_spacing = 5
    bullet_indent = 12
    normal_font_size = 12
    section_font_size = 15
    name_font_size = 20
    contact_font_size = 11

    lines = [line.strip() for line in md_text.split('\n') if line.strip()]
    i = 0

    # Name (first line, bold, large)
    if lines and (lines[0].startswith("**") and lines[0].endswith("**")):
        name = lines[0].strip("*")
        pdf.set_font('DejaVu', 'B', name_font_size)
        pdf.cell(0, 12, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        i += 1
    else:
        pdf.set_font('DejaVu', 'B', name_font_size)
        pdf.cell(0, 12, "Name Missing", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Contact Info (second line, smaller, gray)
    if i < len(lines) and "|" in lines[i]:
        pdf.set_font('DejaVu', '', contact_font_size)
        pdf.set_text_color(90, 90, 90)
        pdf.cell(0, 8, lines[i], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        i += 1
    pdf.set_text_color(0, 0, 0)

    # Horizontal line
    pdf.ln(2)
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.5)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(4)

    # Main content
    section_titles = ["summary", "experience", "education", "skills", "projects", "certifications"]
    while i < len(lines):
        line = lines[i]

        # Section header
        if line.lower().startswith("##"):
            section_title = line.lstrip('#').strip()
            pdf.ln(section_spacing)
            pdf.set_font('DejaVu', 'B', section_font_size)
            pdf.cell(0, 10, section_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
            pdf.set_font('DejaVu', '', normal_font_size)
            i += 1
            continue

        # Company/role line (italic or bold, with | or parentheses)
        if (line.startswith("*") and line.endswith("*")) or (" | " in line and not line.startswith("-")):
            pdf.set_font('DejaVu', 'I', normal_font_size)
            pdf.multi_cell(0, line_height, line.replace("*", ""))
            pdf.set_font('DejaVu', '', normal_font_size)
            i += 1
            continue

        # Bullets
        if line.startswith("•") or line.startswith("- ") or line.startswith("* "):
            bullet_text = line.lstrip("•- *")
            pdf.set_x(pdf.l_margin + bullet_indent)
            pdf.set_font('DejaVu', '', normal_font_size)
            pdf.multi_cell(0, line_height, u"\u2022 " + bullet_text)
            i += 1
            continue

        # Skills/Other inline lists (Languages: ...)
        if ":" in line and any(title in line.lower() for title in ["language", "other", "tool", "technology"]):
            pdf.set_font('DejaVu', 'B', normal_font_size)
            label, rest = line.split(":", 1)
            pdf.write(line_height, label + ":")
            pdf.set_font('DejaVu', '', normal_font_size)
            pdf.write(line_height, rest.strip())
            pdf.ln(line_height)
            i += 1
            continue

        # Default: normal text
        pdf.set_font('DejaVu', '', normal_font_size)
        pdf.multi_cell(0, line_height, line)
        i += 1

    pdf.output(output_path)
    print(f"[PDF] Successfully wrote PDF to {output_path}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/review", methods=["POST"])
def review():
    f = request.files['file']
    input_filename = os.path.join(BASE_DIR, f"input_{uuid.uuid4().hex}.pdf")
    output_filename = os.path.join(BASE_DIR, f"improved_{uuid.uuid4().hex}.pdf")
    print(f"[REVIEW] Saving uploaded file as: {input_filename}")
    f.save(input_filename)
    try:
        review_text, improved_resume_md = review_and_improve_resume(input_filename)
        print("[DEBUG] improved_resume_md content:")
        print(improved_resume_md)
        if not improved_resume_md or not improved_resume_md.strip():
            print("[ERROR] Improved Markdown from Gemini is empty!")
            os.remove(input_filename)
            return jsonify({"review": "Gemini did not return an improved resume. Please try again."}), 500

        print(f"[REVIEW] Calling markdown_to_pdf with output: {output_filename}")
        markdown_to_pdf(improved_resume_md, output_filename)
        file_exists = os.path.exists(output_filename)
        print(f"[REVIEW] File exists after PDF creation: {file_exists}")
        os.remove(input_filename)
        return jsonify({
            "review": review_text,
            "pdf_url": f"/download/{os.path.basename(output_filename)}"
        })
    except Exception as e:
        # Improved error handling for Gemini API quota exceeded
        if "ResourceExhausted" in str(e) or "429" in str(e) or "quota" in str(e).lower():
            print("[ERROR] Gemini API quota exceeded.")
            if os.path.exists(input_filename):
                os.remove(input_filename)
            if os.path.exists(output_filename):
                os.remove(output_filename)
            return jsonify({
                "review": "You have exceeded your daily Gemini API quota. Please try again tomorrow or upgrade your plan."
            }), 429
        print(traceback.format_exc())
        if os.path.exists(input_filename):
            os.remove(input_filename)
        if os.path.exists(output_filename):
            os.remove(output_filename)
        return jsonify({"review": "An error occurred processing your resume."}), 500

@app.route("/download/<filename>")
def download_improved_resume(filename):
    if not filename.endswith('.pdf') or '/' in filename or '\\' in filename:
        print(f"[DOWNLOAD] Invalid filename requested: {filename}")
        return "Invalid file.", 400
    file_path = os.path.join(BASE_DIR, filename)
    print(f"[DOWNLOAD] Looking for file: {file_path}")
    file_exists = os.path.exists(file_path)
    print(f"[DOWNLOAD] File exists: {file_exists}")
    if not file_exists:
        return "File not found.", 404

    print(f"[DOWNLOAD] Sending file: {file_path}")
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[STARTUP] Running Flask app at http://0.0.0.0:{port}/")
    app.run(host="0.0.0.0", port=port, debug=True)
