# backend/app.py
from flask import Flask, request, jsonify, render_template
import os
from transcribe import transcribe_audio_file
from analyze import analyze_meeting_content

app = Flask(
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    return transcribe_audio_file()

@app.route('/analyze', methods=['POST'])
def analyze_transcript():
    return analyze_meeting_content()

if __name__ == '__main__':
    app.run(debug=True)
