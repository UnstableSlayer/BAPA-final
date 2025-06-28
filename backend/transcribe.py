import openai
import tempfile
import os
from pathlib import Path
import textwrap
import re

openai.api_key = os.getenv("OPENAI_API_KEY")

def chunk_text(text, max_tokens=2000):
    """Split text into chunks of approximately max_tokens characters."""
    return textwrap.wrap(text, width=max_tokens, break_long_words=False)

def extract_last_speaker_lines(text, num_lines=3):
    """Extract last few speaker-labeled lines to carry speaker context."""
    lines = [line for line in text.strip().splitlines() if line.strip()]
    speaker_lines = [line for line in lines if re.match(r'^Speaker \d+:', line)]
    return speaker_lines[-num_lines:] if speaker_lines else []

def transcribe_audio_file(file):
    """
    Transcribe audio file using Whisper and identify speakers consistently across chunks using GPT-4.
    """
    # Detect file extension
    if hasattr(file, 'filename'):
        filename = file.filename
        file_extension = Path(filename).suffix.lower()
    elif hasattr(file, 'name'):
        filename = file.name if hasattr(file, 'name') else str(file)
        file_extension = Path(filename).suffix.lower()
    else:
        filename = str(file)
        file_extension = Path(filename).suffix.lower()

    supported_formats = {
        '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a',
        '.wav', '.webm', '.ogg', '.flac'
    }

    if file_extension not in supported_formats:
        raise ValueError(f"Unsupported audio format: {file_extension}")

    try:
        # Handle different file types
        if hasattr(file, 'read'):
            if hasattr(file, 'seek'):
                file.seek(0)
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(file.read())
                temp_file_path = temp_file.name
            with open(temp_file_path, 'rb') as audio_file:
                result = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            os.remove(temp_file_path)
        elif os.path.isfile(str(file)):
            with open(file, 'rb') as audio_file:
                result = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
        else:
            raise ValueError("Invalid file input. Expected file path or file-like object.")

        raw_transcript = result
        chunks = chunk_text(raw_transcript, max_tokens=2000)

        speaker_context = []  # Stores speaker lines to help GPT maintain consistency
        final_output = []

        for i, chunk in enumerate(chunks):
            system_prompt = (
                "You are a helpful assistant that adds speaker labels to transcripts. "
                "Use 'Speaker 1:', 'Speaker 2:', etc. and keep them consistent across all chunks. "
                "Use the previous context if available to maintain speaker identity. "
                "DO NOT summarize or change any content."
            )

            context_intro = "\n".join(speaker_context[-3:]) if speaker_context else ""

            messages = [
                {"role": "system", "content": system_prompt},
            ]

            if context_intro:
                messages.append({"role": "user", "content": f"Previous speaker context:\n{context_intro}"})
            
            messages.append({"role": "user", "content": f"Transcript:\n{chunk}"})

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3
            )

            chunk_result = response.choices[0].message.content.strip()
            final_output.append(chunk_result)

            # Update speaker context from current chunk
            speaker_context = extract_last_speaker_lines(chunk_result)

        return "\n\n".join(final_output)

    except openai.APIError as e:
        raise Exception(f"OpenAI API error: {str(e)}")
    except FileNotFoundError:
        raise Exception(f"Audio file not found: {file}")
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")
