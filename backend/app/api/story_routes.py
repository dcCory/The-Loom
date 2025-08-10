# This file will contain all API endpoints related to story generation.

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    GenerateTextRequest, GenerateTextResponse, ModelLoadRequest, ModelLoadResponse,
    StoryTextRequest, StoryTextResponse
)
from app.core.model_manager import load_model, generate_text
from app.core import persistence

router = APIRouter()

@router.get("/test")
async def test_story_endpoint():
    """
    A simple test endpoint for the story API.
    """
    return {"message": "Story API endpoint is working!"}

@router.post("/load_model", response_model=ModelLoadResponse)
async def load_ai_model(request: ModelLoadRequest):
    """
    Endpoint to load an AI model into memory.
    """
    response = await load_model(request.model_id, request.device, request.model_type)
    if response["status"] == "error":
        raise HTTPException(status_code=500, detail=response["message"])
    return response

@router.post("/generate", response_model=GenerateTextResponse)
async def generate_story_text(request: GenerateTextRequest):
    """
    Endpoint to generate text using the loaded AI model.
    """
    generated_content = await generate_text(
        prompt=request.prompt,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        top_k=request.top_k,
        top_p=request.top_p,
        model_type="primary", # Assuming primary model for main generation
        selected_character_ids=request.selected_character_ids, # Pass character IDs
        selected_plot_point_ids=request.selected_plot_point_ids # Pass plot point IDs
    )
    if "Error:" in generated_content:
        raise HTTPException(status_code=500, detail=generated_content)
    return {"generated_text": generated_content}

#-- Endpoints for Main Story Text Persistence ---

@router.put("/main_text", response_model=StoryTextResponse)
async def update_main_story_text(request: StoryTextRequest):
    """
    Updates and saves the main story text.
    """
    persistence.save_main_story_text(request.text)
    return {"text": request.text}

@router.get("/main_text", response_model=StoryTextResponse)
async def get_main_story_text():
    """
    Retrieves the current main story text.
    """
    text = persistence.load_main_story_text()
    return {"text": text}