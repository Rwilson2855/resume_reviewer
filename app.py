import os
import uuid
import traceback
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file
from gemini_api import review_and_improve_resume, markdown_to_pdf

load_dotenv()
app = Flask(__name__)

# Always use the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

    # No deletion here for debugging!
    print(f"[DOWNLOAD] Sending file: {file_path}")
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[STARTUP] Running Flask app at http://0.0.0.0:{port}/")
    app.run(host="0.0.0.0", port=port, debug=True)
