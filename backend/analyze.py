import openai
import os
from flask import request, jsonify

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_meeting_content():
    data = request.get_json()
    transcript_text = data.get("transcript")

    if not transcript_text:
        return jsonify({"error": "Transcript text is required"}), 400

    try:
        functions = [
            {
                "name": "schedule_meeting_task",
                "description": "Create a task or calendar event from the meeting.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string"},
                        "assignee": {"type": "string"},
                        "due_date": {"type": "string", "format": "date"}
                    },
                    "required": ["task", "assignee"]
                }
            }
        ]

        response = openai.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {
                    "role": "system",
                    "content": "You are a meeting assistant. Summarize the transcript, extract decisions, action items, and assign owners."
                },
                {"role": "user", "content": transcript_text}
            ],
            functions=functions,
            function_call="auto"
        )

        return jsonify(response.choices[0].message.content)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
