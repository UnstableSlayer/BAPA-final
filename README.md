# Meeting Analyzer - Project Documentation

## Overview

The Meeting Analyzer is a comprehensive Flask-based web application that processes meeting recordings to extract actionable insights, manage tasks and calendar events, and provide AI-powered analysis. The system uses OpenAI's APIs for transcription, analysis, and visualization to transform meeting audio into structured, actionable data.

## Features

- **Audio Transcription**: Converts meeting recordings to text with speaker identification
- **Intelligent Analysis**: Extracts tasks, calendar events, and meeting insights
- **Task Management**: Automatically creates, updates, and tracks action items
- **Calendar Integration**: Manages meeting events and schedules
- **Meeting Effectiveness Prediction**: AI-powered assessment of meeting productivity
- **Semantic Search**: Find relevant tasks and events using natural language queries
- **Visual Presentations**: Generate presentation slides from meeting content

## Architecture

### Core Components

1. **Flask Web Application** (`backend/app.py`) - Main web server and API endpoints
2. **Audio Transcription** (`backend/transcribe.py`) - Whisper-based audio processing
3. **Content Analysis** (`backend/analyze.py`) - GPT-4 powered meeting analysis
4. **Task & Calendar Management** (`backend/analyze.py`) - Data persistence and CRUD operations
5. **Effectiveness Prediction** (`backend/predict.py`) - Meeting quality assessment
6. **Semantic Search** (`backend/semantic_search.py`) - FAISS-based similarity search
7. **Visualization** (`backend/visualize.py`) - AI-generated presentation slides

### Data Flow

```
Audio File → Transcription → Analysis → Action Extraction → Data Storage
                ↓
         Semantic Indexing → Search Capabilities
                ↓
         Effectiveness Prediction → Quality Metrics
                ↓
         Visualization → Presentation Slides
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Required Python packages (see requirements below)

### Environment Setup

```bash
# Set OpenAI API Key
export OPENAI_API_KEY="your-openai-api-key"

# Install dependencies
pip install flask openai faiss-cpu numpy
```

### Required Dependencies

```
flask
openai
faiss-cpu
numpy
pathlib
tempfile
textwrap
re
json
os
datetime
statistics
```

### Directory Structure

```
project/
├── app.py                 # Main Flask application
├── transcribe.py          # Audio transcription module
├── analyze.py             # Meeting analysis and data management
├── predict.py             # Meeting effectiveness prediction
├── semantic_search.py     # Semantic search functionality
├── visualize.py           # Presentation generation
├── data/                  # Data storage directory
│   ├── calendar.json      # Calendar events storage
│   ├── tasks.json         # Tasks storage
│   ├── search_entries.json # Search index entries
│   └── search_index.faiss # FAISS search index
├── templates/             # HTML templates
└── static/               # Static assets
```

## API Endpoints

### Main Application Routes

#### `GET /`
- **Description**: Main dashboard displaying calendar and tasks
- **Returns**: HTML template with current calendar and task data
- **Error Handling**: Returns JSON error if data loading fails

#### `POST /transcribe`
- **Description**: Transcribe audio file to text with speaker identification
- **Input**: Multipart form data with audio file
- **Supported Formats**: .mp3, .mp4, .mpeg, .mpga, .m4a, .wav, .webm, .ogg, .flac
- **Returns**: `{'transcript': 'transcribed_text'}`
- **Error Handling**: Returns 400 if no file provided, 500 for processing errors

#### `POST /analyze`
- **Description**: Analyze transcript and extract actionable items
- **Input**: `{'transcript': 'meeting_transcript'}`
- **Returns**: Analysis results with extracted tasks, events, and summaries
- **Side Effects**: Creates/updates tasks and calendar events, resets search index

#### `POST /predict`
- **Description**: Predict meeting effectiveness using AI analysis
- **Input**: `{'transcript': 'meeting_transcript'}`
- **Returns**: `{'prediction': 'effectiveness_score_and_analysis'}`

#### `POST /semantic_search`
- **Description**: Search for similar tasks and events using semantic matching
- **Input**: `{'transcript': 'search_query'}`
- **Returns**: `{'search_results': [matching_items]}`

#### `POST /visualize`
- **Description**: Generate presentation slides from meeting transcript
- **Input**: `{'transcript': 'meeting_transcript'}`
- **Returns**: `{'slides': [slide_data_with_images]}`

#### `GET /calendar`
- **Description**: Retrieve all calendar events
- **Returns**: Calendar data in JSON format

#### `GET /tasks`
- **Description**: Retrieve all tasks
- **Returns**: Tasks data in JSON format

## Core Modules

### Audio Transcription (`transcribe.py`)

**Key Functions:**

- `transcribe_audio_file(file)`: Main transcription function
  - Uses OpenAI Whisper for audio-to-text conversion
  - Adds speaker identification using GPT-4
  - Processes large files in chunks to maintain context
  - Supports multiple audio formats

**Features:**
- Automatic speaker labeling
- Context preservation across chunks
- Robust error handling
- Support for various audio formats

### Meeting Analysis (`analyze.py`)

**Key Functions:**

- `analyze_transcript(transcript_text, chunk_size=4000)`: Main analysis function
  - Processes large transcripts in chunks
  - Extracts actionable items (tasks, calendar events)
  - Removes duplicates across chunks
  - Executes CRUD operations automatically

**Data Management Functions:**
- `add_task()`, `update_task()`, `delete_task()`
- `add_calendar_event()`, `update_calendar_event()`, `delete_calendar_event()`
- `load_calendar()`, `save_calendar()`, `load_tasks()`, `save_tasks()`

**Action Types Supported:**
- Create new tasks
- Update existing tasks (status, assignee, due date)
- Delete tasks
- Create new calendar events
- Update existing calendar events (reschedule, attendees)
- Delete calendar events

### Meeting Effectiveness Prediction (`predict.py`)

**Key Function:**

- `predict_meeting_effectiveness(transcript_text, chunk_size=4000)`
  - Analyzes meeting quality using GPT-4
  - Processes large transcripts in chunks
  - Provides numerical effectiveness score (1-10)
  - Generates detailed justification

**Scoring Methodology:**
- Weighted average of chunk scores
- Later chunks weighted slightly higher
- Consolidated analysis across all chunks
- Standard deviation calculation for consistency

### Semantic Search (`semantic_search.py`)

**Key Functions:**

- `search_similar(query, top_k=5)`: Find semantically similar items
- `reset_index()`: Rebuild search index from current data
- `index_all()`: Index all tasks and calendar events

**Technology Stack:**
- OpenAI text-embedding-3-small for embeddings
- FAISS for similarity search
- Automatic deduplication
- Persistent index storage

### Visualization (`visualize.py`)

**Key Function:**

- `generate_presentation_slides(transcript_text, chunk_size=4000)`
  - Extracts key concepts from meeting
  - Generates visual concepts for slides
  - Creates presentation images using DALL-E
  - Returns structured slide data with URLs

## Data Storage

### File-Based Storage System

The application uses JSON files for data persistence:

#### Calendar Data (`data/calendar.json`)
```json
{
  "events": [
    {
      "id": 1,
      "title": "Project Review",
      "date": "2024-12-15",
      "time": "14:00",
      "duration": "1 hour",
      "attendees": ["John", "Sarah"],
      "created_at": "2024-12-01T10:00:00",
      "updated_at": "2024-12-01T15:30:00"
    }
  ],
  "created_at": "2024-12-01T09:00:00"
}
```

#### Tasks Data (`data/tasks.json`)
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Update documentation",
      "description": "Complete API documentation review",
      "assignee": "John Doe",
      "due_date": "2024-12-20",
      "priority": "high",
      "status": "pending",
      "created_at": "2024-12-01T10:00:00",
      "updated_at": "2024-12-01T15:30:00"
    }
  ],
  "created_at": "2024-12-01T09:00:00"
}
```

### Search Index Storage

- `data/search_entries.json`: Metadata for indexed items
- `data/search_index.faiss`: FAISS binary index file

## Usage Examples

### Basic Meeting Processing Workflow

1. **Upload Audio**: Send audio file to `/transcribe` endpoint
2. **Get Transcript**: Receive speaker-labeled transcript
3. **Analyze Content**: Send transcript to `/analyze` endpoint
4. **Review Results**: Check extracted tasks and events
5. **Search Content**: Use `/semantic_search` for finding related items
6. **Assess Quality**: Use `/predict` for effectiveness scoring
7. **Create Presentation**: Use `/visualize` for slide generation

### Example API Calls

```javascript
// Transcribe audio
const formData = new FormData();
formData.append('audio', audioFile);
const transcript = await fetch('/transcribe', {
    method: 'POST',
    body: formData
}).then(r => r.json());

// Analyze transcript
const analysis = await fetch('/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({transcript: transcript.transcript})
}).then(r => r.json());

// Search for related items
const searchResults = await fetch('/semantic_search', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({transcript: "project deadline tasks"})
}).then(r => r.json());
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for all AI features
- `FLASK_ENV`: Set to 'development' for debug mode

### Adjustable Parameters

- **Chunk Size**: Default 4000 characters for transcript processing
- **Search Results**: Default top 5 similar items
- **Image Generation**: Default 1024x1024 slide images
- **Max Slides**: Limited to 8 slides per presentation

## Performance Considerations

### Chunking Strategy
- Large transcripts processed in 4000-character chunks
- Sentence boundary preservation
- Context carried between chunks for consistency

### Deduplication
- Automatic removal of duplicate actionable items
- Signature-based duplicate detection
- Cross-chunk consistency checks

### Search Optimization
- FAISS indexing for fast similarity search
- Persistent index storage
- Automatic re-indexing on data changes

## Security Considerations

- OpenAI API key should be kept secure
- File uploads should be validated
- Consider rate limiting for production deployment
- Audio files are temporarily stored and cleaned up

## Troubleshooting

### Debug Mode

Run with debug enabled:
```bash
FLASK_ENV=development python app.py
```

## Test Cases

### Files
1. **Test cases** (`tests/app-tests.py`) - Tests each feature
2. **Example transcripts** (`transcripts/`) - Transcripts used for demo and test cases.

### Running Tests
```bash
python tests/app-tests.py
```


## Difficulties

### Processing long transcriptions
Processing long transcriptions (30 minutes+) are supported via splitting transcript into clusters, however it takes significant time to process.

### Slide image generation
While as requested in requirements, visual summary generation was implemented, DALL-E 3 can not really generate good enough images to be understandable.