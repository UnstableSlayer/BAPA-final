import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_presentation_slides(transcript_text, chunk_size=4000):
    """Generate presentation slides from transcript chunks with optimal slide count"""
    
    if not transcript_text or not transcript_text.strip():
        return {"error": "No transcript text provided", "images": []}
    
    # Split transcript into chunks
    def split_transcript(text, max_chunk_size):
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence_with_period = sentence + ('.' if sentence != sentences[-1] else '')
            if len(current_chunk + sentence_with_period) <= max_chunk_size:
                current_chunk += sentence_with_period
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence_with_period
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
    
    chunks = split_transcript(transcript_text, chunk_size)
    
    # Extract key concepts from all chunks
    concept_prompt = f"""Analyze these {len(chunks)} meeting transcript chunks and extract key presentation concepts.
    Return JSON with slide concepts that visualize the meeting's main points:
    {{
        "total_slides": 3,
        "slides": [
            {{"title": "Slide title", "concept": "Visual concept description for image generation", "chunk_source": [1,2]}},
            {{"title": "Slide title", "concept": "Visual concept description", "chunk_source": [2,3]}}
        ]
    }}
    
    Chunks: {' | '.join(f'Chunk {i+1}: {chunk[:200]}...' for i, chunk in enumerate(chunks))}"""
    
    try:
        concept_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": concept_prompt}],
            temperature=0.3
        )
        
        content = concept_response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        
        slide_data = json.loads(content)
        slides = slide_data.get("slides", [])
        
        # Limit slides to reasonable number
        slides = slides[:min(len(slides), 8)]
        
    except (json.JSONDecodeError, Exception):
        # Fallback: create one slide per chunk (max 5)
        slides = [{"title": f"Key Points {i+1}", "concept": f"Visual summary of meeting section {i+1}: {chunk[:150]}", "chunk_source": [i+1]} 
                 for i, chunk in enumerate(chunks[:5])]
    
    # Generate images for each slide
    images = []
    for i, slide in enumerate(slides):
        try:
            # Create focused prompt for presentation slide
            image_prompt = f"Professional presentation slide visualization: {slide['concept']}. Clean, business-appropriate diagram or infographic style."
            
            response = openai.images.generate(
                prompt=image_prompt,
                n=1,
                size="1024x1024"
            )
            
            images.append({
                "slide_number": i + 1,
                "title": slide["title"],
                "url": response.data[0].url,
                "concept": slide["concept"],
                "source_chunks": slide.get("chunk_source", [])
            })
            
        except Exception as e:
            print(f"Error generating image for slide {i+1}: {e}")
            continue
    
    return {
        "total_slides": len(images),
        "chunks_processed": len(chunks),
        "images": images
    }