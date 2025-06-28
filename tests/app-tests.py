import pytest
import os
import sys
import json
import tempfile
from unittest.mock import Mock, patch, mock_open

# Get the backend directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
# Add the backend directory to sys.path
sys.path.insert(0, parent_dir)

from transcribe import transcribe_audio_file
from analyze import analyze_transcript, add_task, add_calendar_event
from predict import predict_meeting_effectiveness
from semantic_search import reset_index, search_similar, add_entry
from visualize import generate_presentation_slides

class TestTranscribe:
    """Test audio transcription functionality"""
    
    def test_transcribe_wav_file(self):
        """Test transcribing a real wav file"""
        audio_file = "transcripts/transcript0.wav"
        if os.path.exists(audio_file):
            result = transcribe_audio_file(audio_file)
            assert isinstance(result, str)
            assert len(result) > 0
            assert "Speaker" in result or len(result.split()) > 5
        else:
            pytest.skip("Audio file transcript0.wav not found")
    
    def test_transcribe_second_wav_file(self):
        """Test transcribing second wav file"""
        audio_file = "transcripts/transcript1.wav"
        if os.path.exists(audio_file):
            result = transcribe_audio_file(audio_file)
            assert isinstance(result, str)
            assert len(result) > 0
        else:
            pytest.skip("Audio file transcript1.wav not found")
    
    def test_unsupported_format(self):
        """Test error handling for unsupported audio format"""
        with pytest.raises(ValueError, match="Unsupported audio format"):
            transcribe_audio_file("fake_file.txt")
    
    @patch('openai.audio.transcriptions.create')
    def test_transcribe_mock_response(self, mock_transcribe):
        """Test transcription with mocked OpenAI response"""
        mock_transcribe.return_value = "Hello, this is a test transcript."
        
        # Create a temporary wav file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(b"fake audio data")
            temp_path = temp_file.name
        
        try:
            with open(temp_path, 'rb') as audio_file:
                result = transcribe_audio_file(temp_path)
            assert "test transcript" in result
        finally:
            os.unlink(temp_path)


class TestAnalyze:
    """Test transcript analysis functionality"""
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('analyze.openai.chat.completions.create')
    def test_analyze_simple_transcript(self, mock_openai, mock_file, mock_exists):
        """Test analyzing a simple transcript"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = '{"events": [], "tasks": []}'
        
        # Mock OpenAI response for actionable items
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([
            {
                "action": "create_task",
                "title": "Follow up with client",
                "description": "Send proposal",
                "assignee": "John",
                "due_date": "2025-07-01",
                "priority": "high"
            }
        ])
        mock_openai.return_value = mock_response
        
        transcript = "John needs to follow up with the client by sending a proposal next week."
        result = analyze_transcript(transcript)
        
        assert isinstance(result, dict)
        assert "function_calls" in result
        assert "actionable_items_found" in result
    
    def test_analyze_empty_transcript(self):
        """Test analyzing empty transcript"""
        result = analyze_transcript("")
        assert result == {"error": "No transcript text provided"}
    
    @patch('analyze.load_calendar')
    @patch('analyze.save_calendar')
    def test_add_calendar_event(self, mock_save, mock_load):
        """Test adding calendar event"""
        mock_load.return_value = {"events": []}
        
        result = add_calendar_event(
            title="Team Meeting",
            date="2025-07-01",
            time="10:00",
            duration="1 hour",
            attendees=["Alice", "Bob"]
        )
        
        assert "Team Meeting" in result
        assert "added" in result
        mock_save.assert_called_once()
    
    @patch('analyze.load_tasks')
    @patch('analyze.save_tasks')
    def test_add_task(self, mock_save, mock_load):
        """Test adding task"""
        mock_load.return_value = {"tasks": []}
        
        result = add_task(
            title="Review document",
            description="Review the project proposal",
            assignee="Alice",
            due_date="2025-07-01",
            priority="medium"
        )
        
        assert "Review document" in result
        assert "Alice" in result
        mock_save.assert_called_once()


class TestPredict:
    """Test meeting effectiveness prediction"""
    
    @patch('predict.openai.chat.completions.create')
    def test_predict_single_chunk(self, mock_openai):
        """Test prediction for short transcript (single chunk)"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Meeting effectiveness: 8/10. The discussion was well-structured with clear outcomes."
        mock_openai.return_value = mock_response
        
        transcript = "We discussed the project timeline and assigned tasks clearly."
        result = predict_meeting_effectiveness(transcript)
        
        assert isinstance(result, str)
        assert "8/10" in result or "effectiveness" in result.lower()
    
    @patch('predict.openai.chat.completions.create')
    def test_predict_multiple_chunks(self, mock_openai):
        """Test prediction for long transcript (multiple chunks)"""
        # Mock responses for chunk analysis
        chunk_response = Mock()
        chunk_response.choices = [Mock()]
        chunk_response.choices[0].message.content = json.dumps({
            "score": 7,
            "justification": "Good structure and clear decisions",
            "key_observations": ["Clear agenda", "Action items identified"]
        })
        
        # Mock response for consolidation
        consolidation_response = Mock()
        consolidation_response.choices = [Mock()]
        consolidation_response.choices[0].message.content = "The meeting was effective with good structure throughout."
        
        mock_openai.side_effect = [chunk_response, chunk_response, consolidation_response]
        
        # Create long transcript (multiple chunks)
        long_transcript = "This is a detailed meeting discussion. " * 500
        result = predict_meeting_effectiveness(long_transcript)
        
        assert isinstance(result, str)
        assert "Overall Meeting Effectiveness" in result
        assert "/10" in result
    
    def test_predict_empty_transcript(self):
        """Test prediction with empty transcript"""
        result = predict_meeting_effectiveness("")
        assert "Error: No transcript text provided" in result


class TestSemanticSearch:
    """Test semantic search functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        # Ensure clean state
        reset_index()
    
    @patch('semantic_search.openai.embeddings.create')
    def test_add_and_search_entry(self, mock_embedding):
        """Test adding entries and searching"""
        # Mock embedding response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1] * 1536  # Mock 1536-dim vector
        mock_embedding.return_value = mock_response
        
        # Add test entry
        add_entry("task", "Review project documentation for client meeting")
        
        # Search for similar content
        results = search_similar("project review")
        
        assert isinstance(results, list)
        # Note: Results might be empty due to mocked embeddings
    
    def test_search_empty_query(self):
        """Test search with empty query"""
        with pytest.raises(Exception):
            search_similar("")
    
    @patch('semantic_search.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_index_tasks_and_calendar(self, mock_file, mock_exists):
        """Test indexing tasks and calendar data"""
        mock_exists.return_value = True
        
        # Mock task data
        task_data = {
            "tasks": [
                {
                    "title": "Test task",
                    "description": "Test description",
                    "assignee": "John",
                    "status": "pending",
                    "due_date": "2025-07-01",
                    "priority": "high"
                }
            ]
        }
        
        # Mock calendar data
        calendar_data = {
            "events": [
                {
                    "title": "Team meeting",
                    "date": "2025-07-01",
                    "time": "10:00",
                    "duration": "1 hour",
                    "attendees": ["Alice", "Bob"]
                }
            ]
        }
        
        mock_file.return_value.read.side_effect = [
            json.dumps(task_data),
            json.dumps(calendar_data)
        ]
        
        reset_index()  # This should trigger indexing
        
        # Verify files were attempted to be read
        assert mock_file.called


class TestVisualize:
    """Test presentation slide generation"""
    
    @patch('visualize.openai.chat.completions.create')
    @patch('visualize.openai.images.generate')
    def test_generate_slides_simple(self, mock_image, mock_chat):
        """Test generating slides for simple transcript"""
        # Mock chat response for slide concepts
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock()]
        mock_chat_response.choices[0].message.content = json.dumps({
            "total_slides": 2,
            "slides": [
                {"title": "Project Overview", "concept": "Project timeline visualization", "chunk_source": [1]},
                {"title": "Action Items", "concept": "Task assignment diagram", "chunk_source": [1]}
            ]
        })
        mock_chat.return_value = mock_chat_response
        
        # Mock image generation response
        mock_image_response = Mock()
        mock_image_response.data = [Mock()]
        mock_image_response.data[0].url = "https://example.com/image1.png"
        mock_image.return_value = mock_image_response
        
        transcript = "We discussed the project timeline and assigned tasks to team members."
        result = generate_presentation_slides(transcript)
        
        assert isinstance(result, dict)
        assert "images" in result
        assert "total_slides" in result
        assert len(result["images"]) <= result["total_slides"]
    
    def test_generate_slides_empty_transcript(self):
        """Test generating slides with empty transcript"""
        result = generate_presentation_slides("")
        assert result["error"] == "No transcript text provided"
        assert result["images"] == []
    
    @patch('visualize.openai.chat.completions.create')
    @patch('visualize.openai.images.generate')
    def test_generate_slides_long_transcript(self, mock_image, mock_chat):
        """Test generating slides for long transcript (multiple chunks)"""
        # Mock responses
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock()]
        mock_chat_response.choices[0].message.content = json.dumps({
            "total_slides": 3,
            "slides": [
                {"title": "Opening Discussion", "concept": "Meeting introduction", "chunk_source": [1]},
                {"title": "Main Topics", "concept": "Key discussion points", "chunk_source": [2]},
                {"title": "Next Steps", "concept": "Action items and follow-up", "chunk_source": [3]}
            ]
        })
        mock_chat.return_value = mock_chat_response
        
        mock_image_response = Mock()
        mock_image_response.data = [Mock()]
        mock_image_response.data[0].url = "https://example.com/slide.png"
        mock_image.return_value = mock_image_response
        
        # Long transcript to trigger chunking
        long_transcript = "This is a comprehensive meeting discussion covering multiple topics. " * 300
        result = generate_presentation_slides(long_transcript)
        
        assert isinstance(result, dict)
        assert "chunks_processed" in result
        assert result["chunks_processed"] > 1


# Integration test
class TestIntegration:
    """Integration tests combining multiple components"""
    
    @patch('analyze.openai.chat.completions.create')
    @patch('predict.openai.chat.completions.create')
    def test_full_workflow_mock(self, mock_predict, mock_analyze):
        """Test full workflow with mocked responses"""
        # Mock analyze response
        analyze_response = Mock()
        analyze_response.choices = [Mock()]
        analyze_response.choices[0].message.content = json.dumps([])
        mock_analyze.return_value = analyze_response
        
        # Mock predict response
        predict_response = Mock()
        predict_response.choices = [Mock()]
        predict_response.choices[0].message.content = "Meeting effectiveness: 7/10"
        mock_predict.return_value = predict_response
        
        transcript = "Team discussed project milestones and assigned tasks."
        
        # Test analyze
        analyze_result = analyze_transcript(transcript)
        assert isinstance(analyze_result, dict)
        
        # Test predict
        predict_result = predict_meeting_effectiveness(transcript)
        assert isinstance(predict_result, str)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])