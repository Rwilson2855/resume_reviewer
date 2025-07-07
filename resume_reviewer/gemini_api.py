import os
import google.generativeai as genai  # Or replace with OpenAI if you prefer

def review_resume(path):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        "This is a resume. Review it and give feedback in Gen Z slang. "
        "If it's bad, say 'bro you're cooked' and explain why. "
        "If it's good, say 'you're chillin'. Give specific improvement tips, all in Zoomer talk."
    )
    sample_doc = genai.upload_file(path=path, mime_type='application/pdf')
    response = model.generate_content([sample_doc, prompt])
    return response.text