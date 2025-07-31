from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from app.models.schemas import Character, CharacterCreate, CharacterUpdate
from app.core import character_store

router = APIRouter()

@router.post("/", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_new_character(character_data: CharacterCreate):
    """
    Creates a new character.
    """
    new_character = character_store.create_character(character_data)
    return new_character

@router.get("/", response_model=List[Character])
async def get_all_characters():
    """
    Retrieves a list of all characters.
    """
    return character_store.get_all_characters()

@router.get("/{character_id}", response_model=Character)
async def get_character_by_id(character_id: UUID):
    """
    Retrieves a single character by ID.
    """
    character = character_store.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@router.put("/{character_id}", response_model=Character)
async def update_existing_character(character_id: UUID, update_data: CharacterUpdate):
    """
    Updates an existing character's details.
    """
    updated_character = character_store.update_character(character_id, update_data)
    if not updated_character:
        raise HTTPException(status_code=404, detail="Character not found")
    return updated_character

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character_by_id(character_id: UUID):
    """
    Deletes a character by ID.
    """
    if not character_store.delete_character(character_id):
        raise HTTPException(status_code=404, detail="Character not found")
    return # FastAPI automatically handles 204 No Content for empty returns