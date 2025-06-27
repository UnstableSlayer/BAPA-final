from flask import Flask, request, jsonify, render_template
from transcribe import transcribe_audio_file
from analyze import analyze_transcript, get_calendar, get_tasks
from semantic_search import reset_index, search_similar

from predict import predict_meeting_effectiveness

import os

app = Flask(__name__, template_folder="../templates", static_folder="../static")

@app.route('/')
def index():
    calendar = get_calendar()
    tasks = get_tasks()
    return render_template("index.html", calendar=calendar, tasks=tasks)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    file = request.files.get('audio')
    if not file or file.filename == '':
        return jsonify({'error': 'No file provided'}), 400
    try:
        transcript = transcribe_audio_file(file)
        return jsonify({'transcript': transcript})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    transcript_text = data.get("transcript", "")

    if not transcript_text:
        return jsonify({"error": "No transcript provided"}), 400
    
    try:
        result = analyze_transcript(transcript_text)
        reset_index()
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    transcript_text = data.get("transcript", "")

    if not transcript_text:
        return jsonify({"error": "No transcript provided"}), 400
    
    try:
        result = predict_meeting_effectiveness(transcript_text)
        return jsonify({"prediction": result})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/semantic_search', methods=['POST'])
def recommend():
    query = request.get_json().get("transcript", "")
    if not query.strip():
        return jsonify({"error": "Empty query"}), 400
    results = search_similar(query)
    return jsonify({"search_results": results})

@app.route('/calendar')
def calendar_view():
    calendar = get_calendar()
    return jsonify(calendar)

@app.route('/tasks')
def tasks_view():
    tasks = get_tasks()
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(debug=True)