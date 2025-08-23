import json
import os
from typing import Dict, List, Optional
from uuid import UUID
from app.models.schemas import Project, ProjectCreate, ProjectListItem, Character, PlotPoint
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
PROJECTS_DIR = os.path.join(DATA_DIR, "projects")

print(f"[DEBUG] persistence: DATA_DIR resolved to: {DATA_DIR}") # NEW DEBUG PRINT
print(f"[DEBUG] persistence: PROJECTS_DIR resolved to: {PROJECTS_DIR}") # NEW DEBUG PRINT

# Ensures the data and projects directories exist
try:
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"[DEBUG] persistence: DATA_DIR '{DATA_DIR}' ensured to exist.")
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    print(f"[DEBUG] persistence: PROJECTS_DIR '{PROJECTS_DIR}' ensured to exist.")
except Exception as e:
    print(f"[ERROR] persistence: Failed to create directories: {e}")
    raise

# --- Project Persistence ---

def _get_project_file_path(project_id: UUID) -> str:
    """Helper to get the file path for a specific project."""
    return os.path.join(PROJECTS_DIR, f"{str(project_id)}.json")

def save_project(project: Project):
    """Saves a complete Project object to its dedicated JSON file."""
    print(f"[DEBUG] persistence: save_project called for Project ID: {project.id}")
    try:
        
        serializable_data = project.model_dump(mode='json')
        
        serializable_data['last_modified'] = datetime.now().isoformat()
        
        file_path = _get_project_file_path(project.id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=4)
        print(f"[DEBUG] persistence: Project '{project.title}' (ID: {project.id}) successfully written to {file_path}")
    except Exception as e:
        print(f"[ERROR] persistence: Error saving Project ID {project.id}: {e}")
        raise

def load_project(project_id: UUID) -> Optional[Project]:
    """Loads a specific Project object from its JSON file."""
    file_path = _get_project_file_path(project_id)
    print(f"[DEBUG] persistence: Attempting to load project from {file_path}.")
    if not os.path.exists(file_path):
        print(f"[DEBUG] persistence: Project file {file_path} does not exist. Returning None.")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Pydantic will deserialize UUIDs and nested models automatically
            loaded_project = Project(**data)
            print(f"[DEBUG] persistence: Loaded Project '{loaded_project.title}' (ID: {loaded_project.id}).")
            return loaded_project
    except json.JSONDecodeError as e:
        print(f"[ERROR] persistence: Error decoding Project JSON from {file_path}: {e}. Returning None.")
        return None
    except Exception as e:
        print(f"[ERROR] persistence: Error loading Project from {file_path}: {e}. Returning None.")
        return None

def get_available_projects() -> List[ProjectListItem]:
    """Scans the projects directory and returns a list of available projects (ID and title)."""
    available_projects: List[ProjectListItem] = []
    print(f"[DEBUG] persistence: Scanning {PROJECTS_DIR} for available projects.")
    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith(".json"):
            project_id_str = os.path.splitext(filename)[0]
            try:
                project_id = UUID(project_id_str)
                file_path = os.path.join(PROJECTS_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # We only need title and ID for the list item
                    title = data.get("title", "Untitled Project")
                    last_modified = data.get("last_modified") # Retrieve last modified
                    available_projects.append(ProjectListItem(id=project_id, title=title, last_modified=last_modified))
            except (ValueError, json.JSONDecodeError) as e:
                print(f"[WARNING] persistence: Skipping malformed project file {filename}: {e}")
            except Exception as e:
                print(f"[ERROR] persistence: Unexpected error processing project file {filename}: {e}")
    print(f"[DEBUG] persistence: Found {len(available_projects)} available projects.")
    return available_projects

def delete_project_file(project_id: UUID) -> bool:
    """Deletes a project file from disk."""
    file_path = _get_project_file_path(project_id)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"[DEBUG] persistence: Project file {file_path} deleted.")
            return True
        except Exception as e:
            print(f"[ERROR] persistence: Error deleting project file {file_path}: {e}")
            return False
    return False