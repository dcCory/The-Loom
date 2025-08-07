# --- CREATES API ROUTES FOR WRITER'S BLOCK BUSTER TOOL ---

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID
from app.models.schemas import (
    SuggestionResponse, NextSceneRequest, CharacterIdeaRequest,
    DialogueSparkerRequest, SettingDetailRequest
)
from app.core import model_manager

router = APIRouter()

@router.post("/suggest-next-scene", response_model=SuggestionResponse)
async def get_next_scene_suggestion(request: NextSceneRequest):
    """
    Provides a concise suggestion for the next scene.
    """
    suggestion = await model_manager.suggest_next_scene(
        current_story_context=request.current_story_context,
        selected_character_ids=request.selected_character_ids,
        selected_plot_point_ids=request.selected_plot_point_ids
    )
    if "Error:" in suggestion:
        raise HTTPException(status_code=500, detail=suggestion)
    return {"suggestion": suggestion}

@router.post("/suggest-character-idea", response_model=SuggestionResponse)
async def get_character_idea_suggestion(request: CharacterIdeaRequest):
    """
    Provides a new character idea or development for an existing character.
    """
    suggestion = await model_manager.suggest_character_idea(
        current_story_context=request.current_story_context,
        selected_character_ids=request.selected_character_ids,
        selected_plot_point_ids=request.selected_plot_point_ids,
        focus_on_existing_character_id=request.focus_on_existing_character_id,
        desired_role=request.desired_role
    )
    if "Error:" in suggestion:
        raise HTTPException(status_code=500, detail=suggestion)
    return {"suggestion": suggestion}

@router.post("/suggest-dialogue-sparker", response_model=SuggestionResponse)
async def get_dialogue_sparker_suggestion(request: DialogueSparkerRequest):
    """
    Provides a spark for dialogue between characters.
    """
    suggestion = await model_manager.suggest_dialogue_sparker(
        current_story_context=request.current_story_context,
        selected_character_ids=request.selected_character_ids,
        selected_plot_point_ids=request.selected_plot_point_ids,
        characters_in_dialogue_ids=request.characters_in_dialogue_ids,
        topic=request.topic
    )
    if "Error:" in suggestion:
        raise HTTPException(status_code=500, detail=suggestion)
    return {"suggestion": suggestion}

@router.post("/suggest-setting-detail", response_model=SuggestionResponse)
async def get_setting_detail_suggestion(request: SettingDetailRequest):
    """
    Provides details to enrich a setting.
    """
    suggestion = await model_manager.suggest_setting_detail(
        current_story_context=request.current_story_context,
        selected_character_ids=request.selected_character_ids,
        selected_plot_point_ids=request.selected_plot_point_ids,
        setting_name=request.setting_name,
        focus_on_aspect=request.focus_on_aspect
    )
    if "Error:" in suggestion:
        raise HTTPException(status_code=500, detail=suggestion)
    return {"suggestion": suggestion}
