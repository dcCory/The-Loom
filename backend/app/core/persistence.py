import json
import os
from typing import Dict
from uuid import UUID
from app.models.schemas import Character, PlotPoint

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
CHARACTERS_FILE = os.path.join(DATA_DIR, "characters.json")
PLOT_POINTS_FILE = os.path.join(DATA_DIR, "plot_points.json")
MAIN_STORY_FILE = os.path.join(DATA_DIR, "main_story.txt")


os.makedirs(DATA_DIR, exist_ok=True)

# --- Character Persistence ---

def save_characters(characters: Dict[UUID, Character]):
    print(f"[DEBUG] persistence: save_characters called with {len(characters)} entries.") # DEBUG PRINT
    """Saves the current characters dictionary to a JSON file."""
    try:
        # Converts UUID keys to strings for JSON serialization
        serializable_data = {str(k): v.model_dump(mode='json') for k, v in characters.items()}
        with open(CHARACTERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=4)
        print(f"[DEBUG] persistence: Characters successfully written to {CHARACTERS_FILE}") # DEBUG PRINT
        print(f"Characters saved to {CHARACTERS_FILE}")
    except Exception as e:
        print(f"[ERROR] persistence: Error saving characters: {e}") # DEBUG PRINT

def load_characters() -> Dict[UUID, Character]:
    print(f"[DEBUG] persistence: Attempting to load characters from {CHARACTERS_FILE}.") # DEBUG PRINT
    """Loads characters from a JSON file."""
    if not os.path.exists(CHARACTERS_FILE):
        print(f"[DEBUG] persistence: {CHARACTERS_FILE} does not exist. Returning empty dict.") # DEBUG PRINT
        return {}
    try:
        with open(CHARACTERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert string keys back to UUIDs and deserialize to Character objects
            loaded_chars = {UUID(k): Character(**v) for k, v in data.items()}
            print(f"[DEBUG] persistence: Loaded {len(loaded_chars)} characters from {CHARACTERS_FILE}.") # DEBUG PRINT
            return loaded_chars
    except json.JSONDecodeError as e:
        print(f"[ERROR] persistence: Error decoding characters JSON from {CHARACTERS_FILE}: {e}") # DEBUG PRINT
        return {}
    except Exception as e:
        print(f"[ERROR] persistence: Error loading characters: {e}") # DEBUG PRINT
        return {}

# --- Plot Point Persistence ---

def save_plot_points(plot_points: Dict[UUID, PlotPoint]):
    """Saves the current plot points dictionary to a JSON file."""
    try:
        serializable_data = {str(k): v.model_dump(mode='json') for k, v in plot_points.items()}
        with open(PLOT_POINTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=4)
        print(f"Plot points saved to {PLOT_POINTS_FILE}")
    except Exception as e:
        print(f"Error saving plot points: {e}")

def load_plot_points() -> Dict[UUID, PlotPoint]:
    """Loads plot points from a JSON file."""
    if not os.path.exists(PLOT_POINTS_FILE):
        return {}
    try:
        with open(PLOT_POINTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {UUID(k): PlotPoint(**v) for k, v in data.items()}
    except json.JSONDecodeError as e:
        print(f"Error decoding plot points JSON from {PLOT_POINTS_FILE}: {e}")
        return {}
    except Exception as e:
        print(f"Error loading plot points: {e}")
        return {}

# --- Main Story Text Persistence ---

def save_main_story_text(text: str):
    """Saves the main story text to a text file."""
    try:
        with open(MAIN_STORY_FILE, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Main story text saved to {MAIN_STORY_FILE}")
    except Exception as e:
        print(f"Error saving main story text: {e}")

def load_main_story_text() -> str:
    """Loads the main story text from a text file."""
    if not os.path.exists(MAIN_STORY_FILE):
        return ""
    try:
        with open(MAIN_STORY_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading main story text: {e}")
        return ""