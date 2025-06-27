import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def predict_meeting_effectiveness(transcript_text):
    prompt = (
        "You are an expert productivity assistant.\n"
        "Analyze the following meeting transcript and rate its overall effectiveness on a scale from 1 to 10.\n"
        "Also provide a 2-3 sentence justification.\n\n"
        f"Transcript:\n{transcript_text}"
    )

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You evaluate meeting effectiveness."},
            {"role": "user", "content": prompt}
        ]
    )

    output = response.choices[0].message.content
    return output
