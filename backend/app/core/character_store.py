from typing import Dict, List, Optional
from uuid import UUID
from app.models.schemas import Character, CharacterCreate, CharacterUpdate

# In-memory store for characters.
# Key: Character UUID, Value: Character object
_characters: Dict[UUID, Character] = {}

def create_character(character_data: CharacterCreate) -> Character:
    """Creates a new character and adds it to the store."""
    new_character = Character(**character_data.model_dump())
    _characters[new_character.id] = new_character
    print(f"Created character: {new_character.name} with ID: {new_character.id}")
    return new_character

def get_character(character_id: UUID) -> Optional[Character]:
    """Retrieves a character by their ID."""
    return _characters.get(character_id)

def get_all_characters() -> List[Character]:
    """Retrieves all characters in the store."""
    return list(_characters.values())

def update_character(character_id: UUID, update_data: CharacterUpdate) -> Optional[Character]:
    """Updates an existing character."""
    character = _characters.get(character_id)
    if not character:
        return None

    # Update fields that are provided in update_data
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(character, key, value)
    
    _characters[character_id] = character # Ensure updated object is stored
    print(f"Updated character with ID: {character_id}")
    return character

def delete_character(character_id: UUID) -> bool:
    """Deletes a character by their ID."""
    if character_id in _characters:
        del _characters[character_id]
        print(f"Deleted character with ID: {character_id}")
        return True
    return False

# --- JSON persistence (will work on later) ---
# To make this persistent, you would add load/save functions:
# import json
# import os

# FILE_PATH = "backend/data/characters.json" # Adjust path as needed

# def _load_characters_from_file():
#     global _characters
#     if os.path.exists(FILE_PATH):
#         with open(FILE_PATH, 'r') as f:
#             data = json.load(f)
#             _characters = {UUID(k): Character(**v) for k, v in data.items()}
#     else:
#         _characters = {}

# def _save_characters_to_file():
#     with open(FILE_PATH, 'w') as f:
#         # Convert UUID keys to strings for JSON serialization
#         json_serializable_data = {str(k): v.model_dump() for k, v in _characters.items()}
#         json.dump(json_serializable_data, f, indent=4)

# # Call this function once when the app starts
# # _load_characters_from_file()