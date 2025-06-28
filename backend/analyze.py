import openai
import json
import os
from datetime import datetime, timedelta

openai.api_key = os.getenv("OPENAI_API_KEY")

def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs('data', exist_ok=True)

def load_calendar():
    """Load calendar data from JSON file, create if doesn't exist"""
    ensure_data_directory()
    calendar_file = 'data/calendar.json'
    
    if not os.path.exists(calendar_file):
        # Create default calendar structure
        default_calendar = {
            "events": [],
            "created_at": datetime.now().isoformat()
        }
        with open(calendar_file, 'w') as f:
            json.dump(default_calendar, f, indent=2)
        return default_calendar
    
    try:
        with open(calendar_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading calendar: {e}. Creating new calendar file.")
        default_calendar = {
            "events": [],
            "created_at": datetime.now().isoformat()
        }
        with open(calendar_file, 'w') as f:
            json.dump(default_calendar, f, indent=2)
        return default_calendar

def save_calendar(calendar_data):
    """Save calendar data to JSON file"""
    ensure_data_directory()
    try:
        with open('data/calendar.json', 'w') as f:
            json.dump(calendar_data, f, indent=2)
    except IOError as e:
        print(f"Error saving calendar: {e}")
        raise

def load_tasks():
    """Load tasks data from JSON file, create if doesn't exist"""
    ensure_data_directory()
    tasks_file = 'data/tasks.json'
    
    if not os.path.exists(tasks_file):
        # Create default tasks structure
        default_tasks = {
            "tasks": [],
            "created_at": datetime.now().isoformat()
        }
        with open(tasks_file, 'w') as f:
            json.dump(default_tasks, f, indent=2)
        return default_tasks
    
    try:
        with open(tasks_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading tasks: {e}. Creating new tasks file.")
        default_tasks = {
            "tasks": [],
            "created_at": datetime.now().isoformat()
        }
        with open(tasks_file, 'w') as f:
            json.dump(default_tasks, f, indent=2)
        return default_tasks

def save_tasks(tasks_data):
    """Save tasks data to JSON file"""
    ensure_data_directory()
    try:
        with open('data/tasks.json', 'w') as f:
            json.dump(tasks_data, f, indent=2)
    except IOError as e:
        print(f"Error saving tasks: {e}")
        raise

def get_calendar():
    """Get calendar events for display"""
    return load_calendar()

def get_tasks():
    """Get tasks for display"""
    return load_tasks()

def get_next_event_id():
    """Get the next available event ID"""
    calendar_data = load_calendar()
    if not calendar_data["events"]:
        return 1
    return max(event["id"] for event in calendar_data["events"]) + 1

def get_next_task_id():
    """Get the next available task ID"""
    tasks_data = load_tasks()
    if not tasks_data["tasks"]:
        return 1
    return max(task["id"] for task in tasks_data["tasks"]) + 1

def add_calendar_event(title, date, time, duration, attendees):
    """Add a new calendar event"""
    calendar_data = load_calendar()
    new_event = {
        "id": get_next_event_id(),
        "title": title,
        "date": date,
        "time": time,
        "duration": duration,
        "attendees": attendees if isinstance(attendees, list) else [attendees],
        "created_at": datetime.now().isoformat()
    }
    calendar_data["events"].append(new_event)
    save_calendar(calendar_data)
    return f"Calendar event '{title}' added for {date} at {time}"

def update_calendar_event(event_id, **updates):
    """Update an existing calendar event"""
    calendar_data = load_calendar()
    for event in calendar_data["events"]:
        if event["id"] == event_id:
            for key, value in updates.items():
                if key in event:
                    event[key] = value
            event["updated_at"] = datetime.now().isoformat()
            save_calendar(calendar_data)
            return f"Calendar event ID {event_id} updated successfully"
    return f"Calendar event ID {event_id} not found"

def delete_calendar_event(event_id):
    """Delete a calendar event"""
    calendar_data = load_calendar()
    original_count = len(calendar_data["events"])
    calendar_data["events"] = [e for e in calendar_data["events"] if e["id"] != event_id]
    if len(calendar_data["events"]) < original_count:
        save_calendar(calendar_data)
        return f"Calendar event ID {event_id} deleted"
    return f"Calendar event ID {event_id} not found"

def add_task(title, description, assignee, due_date, priority):
    """Add a new task"""
    tasks_data = load_tasks()
    new_task = {
        "id": get_next_task_id(),
        "title": title,
        "description": description,
        "assignee": assignee,
        "due_date": due_date,
        "priority": priority.lower() if priority else "medium",
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    tasks_data["tasks"].append(new_task)
    save_tasks(tasks_data)
    return f"Task '{title}' assigned to {assignee} with due date {due_date}"

def update_task(task_id, **updates):
    """Update an existing task"""
    tasks_data = load_tasks()
    for task in tasks_data["tasks"]:
        if task["id"] == task_id:
            for key, value in updates.items():
                if key in task:
                    task[key] = value
            task["updated_at"] = datetime.now().isoformat()
            save_tasks(tasks_data)
            return f"Task ID {task_id} updated successfully"
    return f"Task ID {task_id} not found"

def delete_task(task_id):
    """Delete a task"""
    tasks_data = load_tasks()
    original_count = len(tasks_data["tasks"])
    tasks_data["tasks"] = [t for t in tasks_data["tasks"] if t["id"] != task_id]
    if len(tasks_data["tasks"]) < original_count:
        save_tasks(tasks_data)
        return f"Task ID {task_id} deleted"
    return f"Task ID {task_id} not found"

def validate_date(date_str):
    """Validate and format date string"""
    if not date_str:
        return None
    try:
        # Try to parse the date to ensure it's valid
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        # If parsing fails, return today's date as fallback
        return datetime.now().strftime("%Y-%m-%d")

def validate_time(time_str):
    """Validate and format time string"""
    if not time_str:
        return "09:00"  # Default time
    try:
        # Try to parse the time to ensure it's valid
        datetime.strptime(time_str, "%H:%M")
        return time_str
    except ValueError:
        return "09:00"  # Default fallback

def analyze_transcript(transcript_text, chunk_size=4000):
    """Enhanced analysis that processes transcript in chunks to handle large documents while avoiding duplicates"""
    
    if not transcript_text or not transcript_text.strip():
        return {"error": "No transcript text provided"}
    
    # Get existing items for context
    try:
        calendar_data = load_calendar()
        tasks_data = load_tasks()
    except Exception as e:
        return {"error": f"Failed to load existing data: {str(e)}"}
    
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
    
    # Collect all actionable items from all chunks
    all_actionable_items = []
    all_summaries = []
    all_decisions = []
    all_action_items = []
    all_follow_up_meetings = []
    
    # Process each chunk
    for i, chunk in enumerate(chunks):
        # Step 1: Extract actionable items from this chunk
        extraction_prompt = f"""Analyze this meeting transcript chunk ({i+1}/{len(chunks)}) and extract ALL actionable items. 

        CONTEXT: This is part of a larger meeting transcript being processed in chunks.
        
        EXISTING CALENDAR EVENTS:
        {json.dumps(calendar_data['events'], indent=2)}

        EXISTING TASKS:
        {json.dumps(tasks_data['tasks'], indent=2)}

        For each actionable item, determine the appropriate action:
        1. CREATE NEW TASK
        2. UPDATE EXISTING TASK (if referencing an existing task by ID, title, or context)
        3. DELETE TASK (if task is cancelled or no longer needed)
        4. CREATE NEW CALENDAR EVENT
        5. UPDATE EXISTING CALENDAR EVENT (if rescheduling, changing details, or adding attendees)
        6. DELETE CALENDAR EVENT (if meeting is cancelled)

        Return ONLY a JSON array with this exact format:
        [
        {{
            "action": "create_task",
            "title": "Task title",
            "description": "Detailed description",
            "assignee": "Person name",
            "due_date": "YYYY-MM-DD",
            "priority": "high/medium/low",
            "chunk_context": "Brief context from this chunk"
        }},
        {{
            "action": "update_task",
            "task_id": 1,
            "title": "New title (optional)",
            "assignee": "New assignee (optional)",
            "status": "completed/in_progress/cancelled",
            "due_date": "YYYY-MM-DD (optional)",
            "chunk_context": "Brief context from this chunk"
        }},
        {{
            "action": "create_calendar",
            "title": "Meeting title",
            "date": "YYYY-MM-DD",
            "time": "HH:MM",
            "duration": "X hours/minutes",
            "attendees": ["person1", "person2"],
            "chunk_context": "Brief context from this chunk"
        }},
        {{
            "action": "update_calendar",
            "event_id": 1,
            "date": "YYYY-MM-DD (optional)",
            "time": "HH:MM (optional)",
            "attendees": ["new", "attendee", "list"] (optional),
            "chunk_context": "Brief context from this chunk"
        }},
        {{
            "action": "delete_task",
            "task_id": 1,
            "chunk_context": "Brief context from this chunk"
        }},
        {{
            "action": "delete_calendar",
            "event_id": 1,
            "chunk_context": "Brief context from this chunk"
        }}
        ]

        Look for keywords like:
        - "postpone", "reschedule", "move the meeting" → UPDATE calendar
        - "cancel", "no longer needed" → DELETE
        - "completed", "done", "finished" → UPDATE task status
        - "reassign", "change assignee" → UPDATE task
        - "new task", "action item" → CREATE task
        - "follow-up meeting", "schedule" → CREATE calendar

        If dates/times are not specified, use reasonable defaults (today's date, 9 AM).
        """

        try:
            # Extract actionable items from this chunk
            extraction_response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": extraction_prompt},
                    {"role": "user", "content": chunk}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            chunk_actionable_items = []
            try:
                content = extraction_response.choices[0].message.content.strip()
                # Remove any markdown formatting if present
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                chunk_actionable_items = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Failed to parse actionable items JSON for chunk {i+1}: {e}")
                chunk_actionable_items = []

            all_actionable_items.extend(chunk_actionable_items)

            # Generate analysis for this chunk
            analysis_prompt = """Analyze this meeting transcript chunk and provide a summary. Return ONLY valid JSON in this exact format:
            {
                "summary": "Summary of key topics discussed in this chunk",
                "decisions": ["Decision 1 made in this chunk", "Decision 2"],
                "action_items": ["Action item 1", "Action item 2"],
                "follow_up_meetings": ["Follow-up meeting 1", "Follow-up meeting 2"]
            }
            """

            analysis_response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": analysis_prompt},
                    {"role": "user", "content": chunk}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            try:
                content = analysis_response.choices[0].message.content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                chunk_analysis = json.loads(content)
                
                all_summaries.append(chunk_analysis.get("summary", ""))
                all_decisions.extend(chunk_analysis.get("decisions", []))
                all_action_items.extend(chunk_analysis.get("action_items", []))
                all_follow_up_meetings.extend(chunk_analysis.get("follow_up_meetings", []))
            except json.JSONDecodeError:
                all_summaries.append(analysis_response.choices[0].message.content)

        except openai.APIError as e:
            print(f"OpenAI API error for chunk {i+1}: {str(e)}")
            continue
        except Exception as e:
            print(f"Error processing chunk {i+1}: {str(e)}")
            continue

    # Step 2: Remove duplicates and consolidate actionable items
    def remove_duplicate_items(items):
        """Remove duplicate actionable items based on similarity"""
        unique_items = []
        seen_items = set()
        
        for item in items:
            # Create a signature for the item based on action, title, and key details
            if item.get("action") == "create_task":
                signature = f"create_task:{item.get('title', '').lower()}:{item.get('assignee', '').lower()}"
            elif item.get("action") == "create_calendar":
                signature = f"create_calendar:{item.get('title', '').lower()}:{item.get('date', '')}:{item.get('time', '')}"
            elif item.get("action") in ["update_task", "delete_task"]:
                signature = f"{item.get('action')}:task_{item.get('task_id')}"
            elif item.get("action") in ["update_calendar", "delete_calendar"]:
                signature = f"{item.get('action')}:event_{item.get('event_id')}"
            else:
                signature = f"{item.get('action')}:{str(item)}"
            
            if signature not in seen_items:
                seen_items.add(signature)
                unique_items.append(item)
        
        return unique_items

    # Remove duplicates
    unique_actionable_items = remove_duplicate_items(all_actionable_items)

    # Step 3: Execute actions
    function_results = []
    for item in unique_actionable_items:
        try:
            action = item.get("action", "")
            
            if action == "create_task":
                result = add_task(
                    title=item.get("title", "Untitled Task"),
                    description=item.get("description", ""),
                    assignee=item.get("assignee", "Unassigned"),
                    due_date=validate_date(item.get("due_date")),
                    priority=item.get("priority", "medium")
                )
                function_results.append({
                    "function": "add_task",
                    "arguments": {k: v for k, v in item.items() if k != "chunk_context"},
                    "result": result
                })
                
            elif action == "update_task":
                updates = {k: v for k, v in item.items() if k not in ["action", "task_id", "chunk_context"] and v is not None}
                if "due_date" in updates:
                    updates["due_date"] = validate_date(updates["due_date"])
                result = update_task(item.get("task_id"), **updates)
                function_results.append({
                    "function": "update_task",
                    "arguments": {k: v for k, v in item.items() if k != "chunk_context"},
                    "result": result
                })
                
            elif action == "delete_task":
                result = delete_task(item.get("task_id"))
                function_results.append({
                    "function": "delete_task",
                    "arguments": {k: v for k, v in item.items() if k != "chunk_context"},
                    "result": result
                })
                
            elif action == "create_calendar":
                result = add_calendar_event(
                    title=item.get("title", "Untitled Meeting"),
                    date=validate_date(item.get("date")),
                    time=validate_time(item.get("time")),
                    duration=item.get("duration", "1 hour"),
                    attendees=item.get("attendees", [])
                )
                function_results.append({
                    "function": "add_calendar_event",
                    "arguments": {k: v for k, v in item.items() if k != "chunk_context"},
                    "result": result
                })
                
            elif action == "update_calendar":
                updates = {k: v for k, v in item.items() if k not in ["action", "event_id", "chunk_context"] and v is not None}
                if "date" in updates:
                    updates["date"] = validate_date(updates["date"])
                if "time" in updates:
                    updates["time"] = validate_time(updates["time"])
                result = update_calendar_event(item.get("event_id"), **updates)
                function_results.append({
                    "function": "update_calendar_event",
                    "arguments": {k: v for k, v in item.items() if k != "chunk_context"},
                    "result": result
                })
                
            elif action == "delete_calendar":
                result = delete_calendar_event(item.get("event_id"))
                function_results.append({
                    "function": "delete_calendar_event",
                    "arguments": {k: v for k, v in item.items() if k != "chunk_context"},
                    "result": result
                })
                
        except Exception as e:
            function_results.append({
                "function": f"{action}",
                "arguments": {k: v for k, v in item.items() if k != "chunk_context"},
                "result": f"Error: {str(e)}"
            })

    # Step 4: Consolidate and deduplicate analysis results
    def deduplicate_list(items):
        """Remove duplicates while preserving order"""
        seen = set()
        unique_items = []
        for item in items:
            item_lower = item.lower().strip()
            if item_lower not in seen and item.strip():
                seen.add(item_lower)
                unique_items.append(item.strip())
        return unique_items

    # Combine and clean up analysis results
    consolidated_summary = " ".join(filter(None, all_summaries))
    unique_decisions = deduplicate_list(all_decisions)
    unique_action_items = deduplicate_list(all_action_items)
    unique_follow_up_meetings = deduplicate_list(all_follow_up_meetings)

    # Create final consolidated analysis
    final_result = {
        "summary": consolidated_summary,
        "decisions": unique_decisions,
        "action_items": unique_action_items,
        "follow_up_meetings": unique_follow_up_meetings,
        "function_calls": function_results,
        "actionable_items_found": len(unique_actionable_items),
        "chunks_processed": len(chunks),
        "duplicates_removed": len(all_actionable_items) - len(unique_actionable_items)
    }

    return final_result

# Additional utility functions for better error handling
def initialize_system():
    """Initialize the system by creating necessary files and directories"""
    try:
        ensure_data_directory()
        load_calendar()  # This will create the file if it doesn't exist
        load_tasks()     # This will create the file if it doesn't exist
        return {"status": "success", "message": "System initialized successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to initialize system: {str(e)}"}

def get_system_status():
    """Get the current status of the system"""
    try:
        calendar_exists = os.path.exists('data/calendar.json')
        tasks_exists = os.path.exists('data/tasks.json')
        calendar_data = load_calendar()
        tasks_data = load_tasks()
        
        return {
            "status": "healthy",
            "files": {
                "calendar": {
                    "exists": calendar_exists,
                    "events_count": len(calendar_data.get("events", []))
                },
                "tasks": {
                    "exists": tasks_exists,
                    "tasks_count": len(tasks_data.get("tasks", []))
                }
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}