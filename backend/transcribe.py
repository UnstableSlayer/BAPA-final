import openai
import tempfile
import subprocess
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def transcribe_audio_file(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        file.save(temp_input.name)
        temp_input_path = temp_input.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
        temp_output_path = temp_output.name

    subprocess.run([
        'ffmpeg', '-i', temp_input_path,
        '-ar', '16000', '-ac', '1', '-f', 'wav', '-y',
        temp_output_path
    ], check=True)

    with open(temp_output_path, 'rb') as audio_file:
        result = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )

    os.remove(temp_input_path)
    os.remove(temp_output_path)

    return result