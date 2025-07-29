import os
import uuid
import traceback
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from dotenv import load_dotenv
from weasyprint import HTML
from gemini_api import review_and_improve_resume

load_dotenv()
app = Flask(__name__)
app.secret_key = 'your-really-secret-key'  # Change this!

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "templates")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/review', methods=['POST'])
def review():
    if 'file' not in request.files:
        flash("No file part in form submission.")
        return redirect(url_for('index'))

    f = request.files['file']
    if f.filename == '':
        flash("No selected file.")
        return redirect(url_for('index'))

    input_filename = os.path.join(UPLOAD_FOLDER, f"input_{uuid.uuid4().hex}.pdf")
    improved_pdf_filename = f"improved_{uuid.uuid4().hex}.pdf"
    improved_pdf_path = os.path.join(STATIC_FOLDER, improved_pdf_filename)

    f.save(input_filename)
    try:
        # Ask Gemini for feedback and improved HTML
        review_text, improved_resume_html = review_and_improve_resume(input_filename)

        if not improved_resume_html or not improved_resume_html.strip():
            os.remove(input_filename)
            flash("Gemini did not return an improved resume. Please try again.")
            return redirect(url_for('index'))

        # Generate the improved PDF using WeasyPrint and your CSS
        css_path = os.path.join(STATIC_FOLDER, "resume.css")
        HTML(string=improved_resume_html, base_url=BASE_DIR).write_pdf(
            improved_pdf_path,
            stylesheets=[css_path]
        )
        os.remove(input_filename)

        return render_template(
            'review_result.html',
            feedback=review_text,
            pdf_url=url_for('static', filename=improved_pdf_filename)
        )
    except Exception as e:
        print(traceback.format_exc())
        if os.path.exists(input_filename):
            os.remove(input_filename)
        flash(f"Error processing resume: {e}")
        return redirect(url_for('index'))

# Optional: direct download endpoint if you want file served as attachment
@app.route("/download/<filename>")
def download_pdf(filename):
    if not filename.endswith('.pdf'):
        return "Invalid file.", 400
    file_path = os.path.join(STATIC_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found.", 404
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)