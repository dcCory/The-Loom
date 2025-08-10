from typing import Dict, List, Optional
from uuid import UUID
from app.models.schemas import Character, CharacterCreate, CharacterUpdate
from app.core import persistence

# In-memory store for characters.
# Key: Character UUID, Value: Character object
_characters: Dict[UUID, Character] = persistence.load_characters()
print(f"[DEBUG] character_store: Initial load, _characters has {len(_characters)} entries.") # DEBUG PRINT

def create_character(character_data: CharacterCreate) -> Character:
    print(f"[DEBUG] character_store: Before creating {character_data.name}, _characters has {len(_characters)} entries.") # DEBUG PRINT
    """Creates a new character and adds it to the store."""
    new_character = Character(**character_data.model_dump())
    _characters[new_character.id] = new_character
    print(f"[DEBUG] character_store: After creating {new_character.name}, _characters has {len(_characters)} entries. Saving...") # DEBUG PRINT
    persistence.save_characters(_characters)
    print(f"[DEBUG] character_store: Saved characters after creating {new_character.name}.") # DEBUG PRINT
    print(f"Created character: {new_character.name} with ID: {new_character.id}")
    return new_character

def get_character(character_id: UUID) -> Optional[Character]:
    """Retrieves a character by their ID."""
    return _characters.get(character_id)

def get_all_characters() -> List[Character]:
    """Retrieves all characters in the store."""
    print(f"[DEBUG] character_store: get_all_characters called, returning {len(_characters)} entries.") # DEBUG PRINT
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
    persistence.save_characters(_characters) #Saves after updating
    print(f"Updated character with ID: {character_id}")
    print(f"[DEBUG] character_store: Saved characters after updating {character_id}.") # DEBUG PRINT
    return character

def delete_character(character_id: UUID) -> bool:
    """Deletes a character by their ID."""
    if character_id in _characters:
        del _characters[character_id]
        persistence.save_characters(_characters) # Save after deletion
        print(f"Deleted character with ID: {character_id}")
        print(f"[DEBUG] character_store: Saved characters after deleting {character_id}.") # DEBUG PRINT
        return True
    return False