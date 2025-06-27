import openai
import faiss
import json
import os
import numpy as np

openai.api_key = os.getenv("OPENAI_API_KEY")

tasks_path = "data/tasks.json"
calendar_path = "data/calendar.json"

DATA_PATH = "data/search_entries.json"
INDEX_PATH = "data/search_index.faiss"
DIM = 1536  # text-embedding-3-small vector size

INDEX = None
ENTRIES = {}  # Maps index => {type, text}

def load_data():
    global ENTRIES
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r') as f:
            ENTRIES = json.load(f)

def save_data():
    with open(DATA_PATH, 'w') as f:
        json.dump(ENTRIES, f, indent=2)

def init_index():
    global INDEX, ENTRIES
    if os.path.exists(INDEX_PATH):
        INDEX = faiss.read_index(INDEX_PATH)
        load_data()
    else:
        reset_index()

def reset_index():
    global INDEX, ENTRIES

    INDEX = faiss.IndexFlatL2(DIM)
    ENTRIES.clear()
    save_data()
    index_all()

def embed_text(text):
    res = openai.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(res.data[0].embedding, dtype='float32')

def add_entry(entry_type, text):
    # Avoid duplicate entries (same type + text)
    for entry in ENTRIES.values():
        if entry["type"] == entry_type and entry["text"] == text:
            print(f"Skipped duplicate entry: {entry_type} → {text[:60]}...")
            return

    vec = embed_text(text)
    INDEX.add(np.array([vec]))
    entry_id = str(len(ENTRIES))
    ENTRIES[entry_id] = {"type": entry_type, "text": text}
    save_data()
    faiss.write_index(INDEX, INDEX_PATH)

def index_all():
    global tasks_path, calendar_path
    # Load and index tasks
    if os.path.exists(tasks_path):
        with open(tasks_path) as f:
            data = json.load(f)
            tasks = data.get("tasks", [])
            for task in tasks:
                text = (
                    f"Task: {task.get('title', '')}; "
                    f"Description: {task.get('description', '')}; "
                    f"Assignee: {task.get('assignee', '')}; "
                    f"Status: {task.get('status', '')}; "
                    f"Due: {task.get('due_date', '')}; "
                    f"Priority: {task.get('priority', '')}"
                )
                add_entry("task", text)

    # Load and index calendar events
    if os.path.exists(calendar_path):
        with open(calendar_path) as f:
            data = json.load(f)
            events = data.get("events", [])
            for event in events:
                attendees = ', '.join(event.get("attendees", []))
                text = (
                    f"Event: {event.get('title', '')}; "
                    f"Date: {event.get('date', '')} at {event.get('time', '')}; "
                    f"Duration: {event.get('duration', '')}; "
                    f"Attendees: {attendees}"
                )
                add_entry("calendar", text)

def search_similar(query, top_k=5):
    vec = embed_text(query)
    D, I = INDEX.search(np.array([vec]), top_k)
    results = []
    for idx in I[0]:
        meta = ENTRIES.get(str(idx))
        if meta:
            results.append(meta)
    return results

# Initialize on import
init_index()