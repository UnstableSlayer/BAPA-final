import openai
import os
import json
import statistics

openai.api_key = os.getenv("OPENAI_API_KEY")

def predict_meeting_effectiveness(transcript_text, chunk_size=4000):
    """
    Analyze meeting effectiveness by processing transcript in chunks and aggregating results
    """
    
    if not transcript_text or not transcript_text.strip():
        return "Error: No transcript text provided"
    
    # Function to split transcript into chunks
    def split_transcript(text, max_chunk_size):
        """Split transcript into chunks at sentence boundaries to preserve context"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Add period back except for the last sentence
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
    
    # Split transcript into manageable chunks
    chunks = split_transcript(transcript_text, chunk_size)
    
    if len(chunks) == 1:
        # If only one chunk, process normally
        prompt = (
            "You are an expert productivity assistant.\n"
            "Analyze the following meeting transcript and rate its overall effectiveness on a scale from 1 to 10.\n"
            "Also provide a 2-3 sentence justification.\n\n"
            f"Transcript:\n{transcript_text}"
        )
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You evaluate meeting effectiveness."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing transcript: {str(e)}"
    
    # Process multiple chunks
    chunk_analyses = []
    chunk_scores = []
    chunk_justifications = []
    
    for i, chunk in enumerate(chunks):
        prompt = (
            f"You are an expert productivity assistant.\n"
            f"Analyze this meeting transcript chunk ({i+1}/{len(chunks)}) and rate its effectiveness on a scale from 1 to 10.\n"
            "IMPORTANT: Return ONLY a JSON object with this exact format:\n"
            "{\n"
            '  "score": 7,\n'
            '  "justification": "2-3 sentence explanation of the rating",\n'
            '  "key_observations": ["observation 1", "observation 2"]\n'
            "}\n\n"
            f"Transcript chunk:\n{chunk}"
        )
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You evaluate meeting effectiveness and return structured JSON responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up JSON formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            try:
                chunk_data = json.loads(content)
                score = chunk_data.get("score", 5)
                justification = chunk_data.get("justification", "No justification provided")
                observations = chunk_data.get("key_observations", [])
                
                chunk_analyses.append({
                    "chunk_number": i + 1,
                    "score": score,
                    "justification": justification,
                    "observations": observations
                })
                
                chunk_scores.append(score)
                chunk_justifications.append(justification)
                
            except json.JSONDecodeError:
                # Fallback: try to extract score from text
                try:
                    import re
                    score_match = re.search(r'(\d+(?:\.\d+)?)', content)
                    score = float(score_match.group(1)) if score_match else 5
                    chunk_scores.append(score)
                    chunk_justifications.append(content)
                    chunk_analyses.append({
                        "chunk_number": i + 1,
                        "score": score,
                        "justification": content,
                        "observations": []
                    })
                except:
                    chunk_scores.append(5)
                    chunk_justifications.append("Unable to parse response")
                    chunk_analyses.append({
                        "chunk_number": i + 1,
                        "score": 5,
                        "justification": "Unable to parse response",
                        "observations": []
                    })
        
        except Exception as e:
            print(f"Error processing chunk {i+1}: {str(e)}")
            chunk_scores.append(5)
            chunk_justifications.append(f"Error processing chunk: {str(e)}")
            chunk_analyses.append({
                "chunk_number": i + 1,
                "score": 5,
                "justification": f"Error processing chunk: {str(e)}",
                "observations": []
            })
    
    # Calculate overall effectiveness
    if chunk_scores:
        # Use weighted average (later chunks might be more important for conclusions)
        weights = [1 + (i * 0.1) for i in range(len(chunk_scores))]  # Slight weight increase for later chunks
        weighted_score = sum(score * weight for score, weight in zip(chunk_scores, weights)) / sum(weights)
        overall_score = round(weighted_score, 1)
        
        # Alternative: simple average
        # overall_score = round(statistics.mean(chunk_scores), 1)
    else:
        overall_score = 5.0
    
    # Generate consolidated justification
    try:
        consolidation_prompt = f"""
        Based on the analysis of {len(chunks)} chunks of a meeting transcript, provide a final assessment.
        
        Chunk scores: {chunk_scores}
        Individual justifications: {chunk_justifications}
        
        Provide a consolidated 2-3 sentence justification for an overall effectiveness score of {overall_score}/10.
        Focus on the most important patterns and themes across all chunks.
        """
        
        consolidation_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You provide consolidated meeting effectiveness assessments."},
                {"role": "user", "content": consolidation_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        consolidated_justification = consolidation_response.choices[0].message.content.strip()
        
    except Exception as e:
        # Fallback justification
        if overall_score >= 8:
            consolidated_justification = f"The meeting demonstrates high effectiveness with an average score of {overall_score}/10 across {len(chunks)} segments. The discussion shows strong structure, clear outcomes, and productive dialogue throughout."
        elif overall_score >= 6:
            consolidated_justification = f"The meeting shows moderate effectiveness with an average score of {overall_score}/10 across {len(chunks)} segments. There are good elements but also areas for improvement in focus and productivity."
        else:
            consolidated_justification = f"The meeting shows low effectiveness with an average score of {overall_score}/10 across {len(chunks)} segments. Significant improvements needed in structure, focus, and actionable outcomes."
    
    # Format final output
    final_output = f"Overall Meeting Effectiveness: {overall_score}/10\n\n"
    final_output += f"Justification: {consolidated_justification}\n\n"
    final_output += f"Analysis Details:\n"
    final_output += f"- Processed {len(chunks)} transcript chunks\n"
    final_output += f"- Individual chunk scores: {chunk_scores}\n"
    final_output += f"- Score range: {min(chunk_scores)}-{max(chunk_scores)}\n"
    final_output += f"- Standard deviation: {round(statistics.stdev(chunk_scores) if len(chunk_scores) > 1 else 0, 2)}"
    
    return final_output