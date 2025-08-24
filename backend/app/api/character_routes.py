from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
# Import Pydantic schemas for data validation and response modeling.
# Character, CharacterCreate, and CharacterUpdate define the structure of character data.
from app.models.schemas import Character, CharacterCreate, CharacterUpdate
# Import the project_manager module. This module is responsible for managing
# the currently active project in memory and delegating persistence operations.
from app.core import project_manager

# Initialize FastAPI's APIRouter.
# This router will handle all API endpoints related to character management.
router = APIRouter()

@router.post("/", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_new_character(character_data: CharacterCreate):
    """
    API endpoint to create a new character for the active project.
    
    Args:
        character_data (CharacterCreate): The data for the new character,
                                         validated by the CharacterCreate schema.
    
    Returns:
        Character: The newly created character object, including its generated ID.
    
    Raises:
        HTTPException: 400 if no project is active, 500 if character creation fails.
    """
    # Attempt to retrieve the currently active project from the project_manager.
    active_project = project_manager.get_active_project()
    # If no project is active, raise an HTTPException to inform the user.
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Please load or create a project first.")
    
    # Add the new character data to the active project via the project_manager.
    # The project_manager assigns a UUID and adds it to the active project's character list.
    new_character = project_manager.add_active_project_character(character_data)
    # If for some reason the character wasn't added (e.g., internal error in project_manager),
    # raise a 500 Internal Server Error.
    if not new_character:
        raise HTTPException(status_code=500, detail="Failed to add character to active project.")
    
    # After modifying the active project (adding a character), save the entire project state to disk.
    # This ensures persistence of the new character.
    await project_manager.save_active_project()
    # Return the newly created character object as the API response.
    return new_character

@router.get("/", response_model=List[Character])
async def get_all_characters():
    """
    API endpoint to retrieve a list of all characters in the active project.
    
    Returns:
        List[Character]: A list of all character objects in the active project.
                        Returns an empty list if no project is active.
    """
    # Attempt to retrieve the currently active project.
    active_project = project_manager.get_active_project()
    # If no project is active, return an empty list, as there are no characters to show.
    if not active_project:
        return []
    
    # Retrieve and return the list of characters from the active project via the project_manager.
    return project_manager.get_active_project_characters()

@router.get("/{character_id}", response_model=Character)
async def get_character_by_id(character_id: UUID):
    """
    API endpoint to retrieve a single character by its ID from the active project.
    
    Args:
        character_id (UUID): The unique identifier of the character to retrieve.
    
    Returns:
        Character: The character object matching the provided ID.
    
    Raises:
        HTTPException: 400 if no project is active, 404 if character is not found.
    """
    # Attempt to retrieve the currently active project.
    active_project = project_manager.get_active_project()
    # If no project is active, raise an HTTPException.
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Cannot retrieve character.")
    
    # Retrieve the specific character from the active project using its ID.
    character = project_manager.get_active_project_character(character_id)
    # If the character is not found in the active project, raise a 404 Not Found error.
    if not character:
        raise HTTPException(status_code=404, detail="Character not found in active project.")
    # Return the found character object.
    return character

@router.put("/{character_id}", response_model=Character)
async def update_existing_character(character_id: UUID, update_data: CharacterUpdate):
    """
    API endpoint to update an existing character's details in the active project.
    
    Args:
        character_id (UUID): The unique identifier of the character to update.
        update_data (CharacterUpdate): The data containing the fields to update,
                                       validated by the CharacterUpdate schema.
    
    Returns:
        Character: The updated character object.
    
    Raises:
        HTTPException: 400 if no project is active, 404 if character is not found.
    """
    # Attempt to retrieve the currently active project.
    active_project = project_manager.get_active_project()
    # If no project is active, raise an HTTPException.
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Cannot update character.")
    
    # Update the character in the active project using its ID and the provided data.
    updated_character = project_manager.update_active_project_character(character_id, update_data)
    # If the character was not found for updating, raise a 404 Not Found error.
    if not updated_character:
        raise HTTPException(status_code=404, detail="Character not found in active project.")
    
    # After modifying the active project (updating a character), save the entire project state to disk.
    await project_manager.save_active_project()
    # Return the updated character object.
    return updated_character

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character_by_id(character_id: UUID):
    """
    API endpoint to delete a character by its ID from the active project.
    
    Args:
        character_id (UUID): The unique identifier of the character to delete.
    
    Returns:
        None: A 204 No Content status is returned upon successful deletion.
    
    Raises:
        HTTPException: 400 if no project is active, 404 if character is not found.
    """
    # Attempt to retrieve the currently active project.
    active_project = project_manager.get_active_project()
    # If no project is active, raise an HTTPException.
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Cannot delete character.")
    
    # Delete the character from the active project.
    # If the character was not found for deletion, raise a 404 Not Found error.
    if not project_manager.delete_active_project_character(character_id):
        raise HTTPException(status_code=404, detail="Character not found in active project.")
    
    # After modifying the active project (deleting a character), save the entire project state to disk.
    await project_manager.save_active_project()
    # FastAPI automatically handles the 204 No Content response for an empty return.
    return