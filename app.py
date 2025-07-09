from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify, send_file, after_this_request
from gemini_api import review_and_improve_resume, text_to_pdf
import os
import uuid
import traceback

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/review", methods=["POST"])
def review():
    f = request.files['file']
    input_filename = f"input_{uuid.uuid4().hex}.pdf"
    output_filename = f"improved_{uuid.uuid4().hex}.pdf"
    f.save(input_filename)
    try:
        review_text, improved_text = review_and_improve_resume(input_filename)
        text_to_pdf(improved_text, output_filename)
        os.remove(input_filename)
        return jsonify({
            "review": review_text,
            "pdf_url": f"/download/{output_filename}"
        })
    except Exception as e:
        print(traceback.format_exc())
        # Clean up files on error
        if os.path.exists(input_filename):
            os.remove(input_filename)
        if os.path.exists(output_filename):
            os.remove(output_filename)
        return jsonify({"review": "An error occurred processing your resume."}), 500

@app.route("/download/<filename>")
def download_improved_resume(filename):
    if not filename.endswith('.pdf') or '/' in filename or '\\' in filename:
        return "Invalid file.", 400
    file_path = os.path.join(os.getcwd(), filename)
    if not os.path.exists(file_path):
        return "File not found.", 404

    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
        return response

    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)