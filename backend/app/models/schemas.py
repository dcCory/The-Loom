# This file will define Pydantic models for data validation.
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from uuid import UUID, uuid4
import json

class GenerateTextRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 100
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.95
    selected_character_ids: Optional[List[UUID]] = None
    selected_plot_point_ids: Optional[List[UUID]] = None

    # Add fields for character_ids, plot_points, etc., later

class GenerateTextResponse(BaseModel):
    generated_text: str

class ModelLoadRequest(BaseModel):
    model_id: str # A file path relative to backend/models
    device: Literal["cpu", "cuda", "hip"] = "cpu" # Explicitly defines allowed devices
    model_type: Literal["primary", "auxiliary"] = "primary"
    inference_library: Literal["transformers", "exllamav2", "llama_cpp"] = "transformers" # Inference library selection

class ModelLoadResponse(BaseModel):
    message: str
    status: str

class CharacterBase(BaseModel):
    """Base schema for Character data."""
    name: str = Field(..., min_length=1, max_length= 100)
    description: str = Field(..., min_length=1)
    traits: Optional[str] = None
    motivations: Optional[str] = None
    physical_appearance: Optional[str] = None
    status: str = "Alive" # Can be "Alive, "Deceased", "Missing", etc.

class CharacterCreate(CharacterBase):
    """Schema for creating a new Character."""
    # No additional fields beyond CharacterBase for creation

class CharacterUpdate(CharacterBase):
    """Schema for updating an existing Character."""
    # All fields are optional for partialy updating a character
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Character(CharacterBase):
    """Complete Character schema including ID, used for response."""
    id: UUID = Field(default_factory=uuid4) #Automatically generates UUIDs for new characters

    class Config:
        fromt_attributes = True #Allows creation from ORM models or objects with attributes


#Plot point tracking schemas

class PlotPointBase(BaseModel):
    """Base schema for Plot Point data."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    status: str = "Planned" # e.g., "Planned", "Completed", "In Progress"
    type: Optional[str] = "Major Plot Beat" # e.g., "Major Plot Beat", "Character Arc", "Subplot"

class PlotPointCreate(PlotPointBase):
    """Schema for creating a new Plot Point."""
    # No additional fields beyond PlotPointBase for creation

class PlotPointUpdate(PlotPointBase):
    """Schema for updating an existing Plot Point."""
    # All fields are optional for partial updates
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None

class PlotPoint(PlotPointBase):
    """Complete Plot Point schema including ID, used for response."""
    id: UUID = Field(default_factory=uuid4) # Auto-generate UUID for new plot points

    class Config:
        from_attributes = True

# --- Writer's Block Buster Schemas ---

class WriterBlockRequest(BaseModel):
    """Base schema for writer's block requests."""
    current_story_context: str = Field(..., description="The relevant portion of the story leading up to the block.")
    selected_character_ids: Optional[List[UUID]] = None
    selected_plot_point_ids: Optional[List[UUID]] = None

class SuggestionResponse(BaseModel):
    """Response schema for AI suggestions."""
    suggestion: str

class NextSceneRequest(WriterBlockRequest):
    """Request to suggest the next scene."""
    pass # Inherits fields from WriterBlockRequest

class CharacterIdeaRequest(WriterBlockRequest):
    """Request to suggest a new character idea."""
    focus_on_existing_character_id: Optional[UUID] = None # Optional: focus on developing an existing character
    desired_role: Optional[str] = None # e.g., "villain", "mentor", "comic relief"

class DialogueSparkerRequest(WriterBlockRequest):
    """Request to spark dialogue."""
    characters_in_dialogue_ids: Optional[List[UUID]] = None # IDs of characters speaking
    topic: Optional[str] = None # What the dialogue should be about

class SettingDetailRequest(WriterBlockRequest):
    """Request to expand on setting details."""
    setting_name: Optional[str] = None # Name of the setting (e.g., "Crystal Caves")
    focus_on_aspect: Optional[str] = None # e.g., "flora", "architecture", "mood"

#-- Schemas for Story Persistence ---

class StoryTextRequest(BaseModel):
    """Request schema for updating the main story text."""
    text: str = Field(..., description="The full current story text.")

class StoryTextResponse(BaseModel):
    """Response schema for retrieving the main story text."""
    text: str

# Schema for listing available model files
class ModelFile(BaseModel):
    filename: str
    path: str # Relative path from backend/models
    size_mb: float
    compatible_libraries: List[Literal["transformers", "exllamav2", "llama_cpp"]]
    suggested_device: Literal["cpu", "cuda", "hip"]
    description: str = ""

class AvailableModelsResponse(BaseModel):
    models: List[ModelFile]
    # flags for backend library availability
    exllamav2_available: bool = False
    llama_cpp_available: bool = False