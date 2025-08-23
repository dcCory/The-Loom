from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from app.models.schemas import Character, CharacterCreate, CharacterUpdate
from app.core import project_manager

router = APIRouter()

@router.post("/", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_new_character(character_data: CharacterCreate):
    """
    Creates a new character for the active project.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Please load or create a project first.")
    
    new_character = project_manager.add_active_project_character(character_data)
    if not new_character:
        raise HTTPException(status_code=500, detail="Failed to add character to active project.")
    
    await project_manager.save_active_project()
    return new_character

@router.get("/", response_model=List[Character])
async def get_all_characters():
    """
    Retrieves a list of all characters in the active project.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        return []
    
    return project_manager.get_active_project_characters()

@router.get("/{character_id}", response_model=Character)
async def get_character_by_id(character_id: UUID):
    """
    Retrieves a single character by ID from the active project.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Cannot retrieve character.")
    
    character = project_manager.get_active_project_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found in active project.")
    return character

@router.put("/{character_id}", response_model=Character)
async def update_existing_character(character_id: UUID, update_data: CharacterUpdate):
    """
    Updates an existing character's details in the active project.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Cannot update character.")
    
    updated_character = project_manager.update_active_project_character(character_id, update_data)
    if not updated_character:
        raise HTTPException(status_code=404, detail="Character not found in active project.")
    
    await project_manager.save_active_project()
    return updated_character

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character_by_id(character_id: UUID):
    """
    Deletes a character by ID from the active project.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Cannot delete character.")
    
    if not project_manager.delete_active_project_character(character_id):
        raise HTTPException(status_code=404, detail="Character not found in active project.")
    
    await project_manager.save_active_project()
    return