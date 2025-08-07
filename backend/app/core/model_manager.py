# This file will handle the loading and management of AI models.
from transformers import AutoTokenizer, AutoModelForCausalLM

# from exllama2 import ExLlamaV2, ExLlamaV2Cache, ExLlamaV2Tokenizer # For ExLlamaV2
import torch
import os

# This is used for when we handle passing the character data to AI context
from typing import Optional, List
from uuid import UUID

# Imported character_store and Character schema
from app.core import character_store
from app.core import plot_store
from app.models.schemas import Character, PlotPoint

# Placeholder for loaded models
# This would be more robust in a production ready app (e.g., using a singleton pattern or dependency injection)
# Global variables will be used for simplicity at the moment.
_primary_model = None
_primary_tokenizer = None
_auxiliary_model = None
_auxiliary_tokenizer = None

async def load_model(model_id: str, device: str, model_type: str):
    """
    Loads an AI model and its tokenizer.
    This is a simplified example. Real-world loading will involve
    checking model types (e.g., ExLlamaV2, Llama.cpp_,
    and more robust error handling.
    """
    global _primary_model, _primary_tokenizer, _auxiliary_model, _auxiliary_tokenizer

    try:
        print(f"Attempting to load model '{model_id}' on device '{device}' for type '{model_type}'...")

        # Example for a small Hugging Face model (e.g., 'gpt2')
        # This will download the model if not cached.
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16) # Use float16 for efficiency

        if device == "cuda" and torch.cuda.is_available():
            model.to("cuda")
            print(f"Model '{model_id}' loaded to CUDA.")
        else:
            model.to("cpu")
            print(f"Model '{model_id}' loaded to CPU.")

        if model_type == "primary":
            _primary_model = model
            _primary_tokenizer = tokenizer
        elif model_type == "auxiliary":
            _auxiliary_model = model
            _auxiliary_tokenizer = tokenizer
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        return {"message": f"Model '{model_id}' ({model_type}) loaded successfully!", "status": "success"}

    except Exception as e:
        print(f"Error loading model '{model_id}': {e}")
        return {"message": f"Failed to load model '{model_id}': {str(e)}", "status": "error"}

async def generate_text(
    prompt: str,
    max_new_tokens: int,
    temperature: float,
    top_k: int,
    top_p: float,
    model_type: str = "primary",
    selected_character_ids: Optional[List[UUID]] = None, #Accepts character IDs for passing context to the AI
    selected_plot_point_ids: Optional[List[UUID]] = None #Accepts plot point IDs for passing context to the AI
) -> str:
    """
    Generates text using the loaded AI model.
    This is a simplified example. Real-world generation will involve
    more sophisticated prompt engineering and context management.
    """
    global _primary_model, _primary_tokenizer, _auxiliary_model, _auxiliary_tokenizer

    model = _primary_model if model_type == "primary" else _auxiliary_model
    tokenizer = _primary_tokenizer if model_type == "primary" else _auxiliary_tokenizer

    if model is None or tokenizer is None:
        return "Error: AI model not loaded. Please load a model first."

    # Fetches and formats character context for AI
    character_context = ""
    if selected_character_ids:
        characters_info: List[str] = []
        for char_id in selected_character_ids:
            character = character_store.get_character(char_id)
            if character:
                # Format character details into a string
                char_str = f"Name:{character.name}"
                if character.description:
                    char_str += f", Description: {character.description}"
                if character.traits:
                    char_str += f", Traist: {character.traits}"
                if character.motivations:
                    char_str += f", Motivations: {character.motivations}"
                if character.physical_appearance:
                    char_str += f", Appearance: {character.physical_appearance}"
                if character.status:
                    char_str += f", Status: {character.status}"
                characters_info.append(char_str)

        if characters_info:
            character_context = "--- Character Information (for context) ---\n"
            character_context += "\n".join(characters_info)
            character_context += "\n-----------------------------------------\n\n"

    # --- Fetch and format plot point context for AI ---
    plot_point_context = ""
    if selected_plot_point_ids:
        plot_points_info: List[str] = []
        for pp_id in selected_plot_point_ids:
            plot_point = plot_store.get_plot_point(pp_id)
            if plot_point:
                pp_str = f"Plot Point: {plot_point.title}"
                if plot_point.description:
                    pp_str += f", Description: {plot_point.description}"
                if plot_point.type:
                    pp_str += f", Type: {plot_point.type}"
                if plot_point.status != "Planned": # Only mention if not 'Planned'
                    pp_str += f", Status: {plot_point.status}"
                plot_points_info.append(pp_str)
        
        if plot_points_info:
            plot_point_context = "--- Plot Point Information (for context) ---\n"
            plot_point_context += "\n".join(plot_points_info)
            plot_point_context += "\n-----------------------------------------\n\n"

    # Combines the character context with the main prompt sent to AI
    full_prompt = character_context + plot_point_context + prompt

    try:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        # Ensure generation parameters are within valid ranges
        temperature = max(0.01, temperature) # Avoid division by zero or log(0)
        top_k = max(1, top_k)
        top_p = max(0.01, min(0.99, top_p)) # Keep top_p between 0.01 and 0.99

        output_tokens = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            do_sample=True, # Enable sampling for creative generation
            pad_token_id=tokenizer.eos_token_id, # Handle padding tokens
            eos_token_id=tokenizer.eos_token_id, # Stop generation at EOS token
        )
        generated_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
        
        # Remove the input prompt from the generated text
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()

        return generated_text

    except Exception as e:
        print(f"Error during text generation: {e}")
        return f"Error during text generation: {str(e)}"
    
#--- Writer's Block Buster Functions ---
async def suggest_next_scene(
    current_story_context: str,
    selected_character_ids: Optional[List[UUID]] = None,
    selected_plot_point_ids: Optional[List[UUID]] = None
) -> str:
    """
    Suggests ideas for the next scene based on current context.
    Uses the auxiliary model.
    """
    prompt = (
        f"Given the following story context:\n'{current_story_context}'\n\n"
        "Suggest a concise and engaging idea for the very next scene. Focus on advancing the plot or character development. "
        "Keep the suggestion brief, a few sentences at most."
    )
    # Use smaller max_new_tokens for concise suggestions
    return await generate_text(
        prompt=prompt,
        max_new_tokens=50,
        temperature=0.8,
        top_k=50,
        top_p=0.95,
        model_type="auxiliary", # IMPORTANT: Use the auxiliary model
        selected_character_ids=selected_character_ids,
        selected_plot_point_ids=selected_plot_point_ids
    )

async def suggest_character_idea(
    current_story_context: str,
    selected_character_ids: Optional[List[UUID]] = None,
    selected_plot_point_ids: Optional[List[UUID]] = None,
    focus_on_existing_character_id: Optional[UUID] = None,
    desired_role: Optional[str] = None
) -> str:
    """
    Suggests a new character idea or development for an existing character.
    Uses the auxiliary model.
    """
    prompt_parts = [f"Given the story context:\n'{current_story_context}'\n\n"]

    if focus_on_existing_character_id:
        character = character_store.get_character(focus_on_existing_character_id)
        if character:
            prompt_parts.append(f"Focus on developing the character '{character.name}' (Description: {character.description}, Traits: {character.traits}).")
            prompt_parts.append("Suggest a new internal conflict, a surprising past event, or a new skill they could acquire.")
        else:
            prompt_parts.append("Suggest a new character idea.")
    else:
        prompt_parts.append("Suggest a new character idea.")
        if desired_role:
            prompt_parts.append(f"The character should ideally serve as a {desired_role}.")
        prompt_parts.append("Provide their name, a brief description, and their potential role in the story.")

    prompt = " ".join(prompt_parts)
    prompt += " Keep the suggestion concise."

    return await generate_text(
        prompt=prompt,
        max_new_tokens=70,
        temperature=0.9,
        top_k=50,
        top_p=0.95,
        model_type="auxiliary",
        selected_character_ids=selected_character_ids,
        selected_plot_point_ids=selected_plot_point_ids
    )

async def suggest_dialogue_sparker(
    current_story_context: str,
    selected_character_ids: Optional[List[UUID]] = None,
    selected_plot_point_ids: Optional[List[UUID]] = None,
    characters_in_dialogue_ids: Optional[List[UUID]] = None,
    topic: Optional[str] = None
) -> str:
    """
    Suggests a spark for dialogue between characters.
    Uses the auxiliary model.
    """
    prompt_parts = [f"Given the current story context:\n'{current_story_context}'\n\n"]
    
    if characters_in_dialogue_ids:
        dialogue_chars = [character_store.get_character(uid) for uid in characters_in_dialogue_ids if character_store.get_character(uid)]
        if dialogue_chars:
            char_names = ", ".join([c.name for c in dialogue_chars])
            prompt_parts.append(f"Imagine a conversation between {char_names}.")
        else:
            prompt_parts.append("Imagine a conversation between unspecified characters.")
    else:
        prompt_parts.append("Imagine a conversation between two characters.")

    if topic:
        prompt_parts.append(f"The dialogue should be about: '{topic}'.")
    
    prompt_parts.append("Provide a brief opening line or a conflict that could spark dialogue.")
    prompt = " ".join(prompt_parts)
    prompt += " Keep it very short and impactful."

    return await generate_text(
        prompt=prompt,
        max_new_tokens=40,
        temperature=0.9,
        top_k=50,
        top_p=0.95,
        model_type="auxiliary",
        selected_character_ids=selected_character_ids,
        selected_plot_point_ids=selected_plot_point_ids
    )

async def suggest_setting_detail(
    current_story_context: str,
    selected_character_ids: Optional[List[UUID]] = None,
    selected_plot_point_ids: Optional[List[UUID]] = None,
    setting_name: Optional[str] = None,
    focus_on_aspect: Optional[str] = None
) -> str:
    """
    Suggests details to enrich a setting.
    Uses the auxiliary model.
    """
    prompt_parts = [f"Given the current story context:\n'{current_story_context}'\n\n"]

    if setting_name:
        prompt_parts.append(f"Focus on the setting: '{setting_name}'.")
    else:
        prompt_parts.append("Describe details for the current setting.")
    
    if focus_on_aspect:
        prompt_parts.append(f"Specifically, elaborate on its {focus_on_aspect}.")
    
    prompt_parts.append("Provide a few descriptive sentences about the atmosphere, objects, or sensory details.")
    prompt = " ".join(prompt_parts)
    prompt += " Keep the description concise."

    return await generate_text(
        prompt=prompt,
        max_new_tokens=60,
        temperature=0.8,
        top_k=50,
        top_p=0.95,
        model_type="auxiliary",
        selected_character_ids=selected_character_ids,
        selected_plot_point_ids=selected_plot_point_ids
    )