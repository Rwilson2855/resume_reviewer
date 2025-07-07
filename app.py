from flask import Flask, render_template, request, jsonify
from gemini_api import review_resume

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/review", methods=["POST"])
def review():
    f = request.files['file']
    f.save('./input.pdf')
    review_text = review_resume('./input.pdf')
    return jsonify({"review": review_text})

if __name__ == "__main__":
    app.run(debug=True)