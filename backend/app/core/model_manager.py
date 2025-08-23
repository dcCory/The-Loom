# This file will handle the loading and management of AI models.
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import glob

# This is used for when we handle passing the character data to AI context
from typing import Optional, List, Dict, Union, Literal
from uuid import UUID

# Import ExLlamaV2 components
try:
    from exllamav2 import ExLlamaV2, ExLlamaV2Cache, ExLlamaV2Tokenizer
    from exllamav2.config import ExLlamaV2Config
    from exllamav2.model import ExLlamaV2Sampler
    EXLLAMAV2_AVAILABLE = True
    print("[DEBUG] ExLlamaV2 is available.")
except ImportError:
    EXLLAMAV2_AVAILABLE = False
    print("[DEBUG] ExLlamaV2 not found. It will not be available for inference.")

# Import llama_cpp components
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
    print("[DEBUG] llama_cpp is available.")
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    print("[DEBUG] llama_cpp not found. It will not be available for inference.")

# Imported character_store and Character schema
from app.core import character_store
from app.core import plot_store
from app.models.schemas import Character, PlotPoint, ModelFile

# Placeholder for loaded models

_primary_model: Optional[Union[AutoModelForCausalLM, "ExLlamaV2", "Llama"]] = None
_primary_tokenizer: Optional[Union[AutoTokenizer, "ExLlamaV2Tokenizer"]] = None
_primary_inference_library: Optional[str] = None


_auxiliary_model: Optional[Union[AutoModelForCausalLM, "ExLlamaV2", "Llama"]] = None
_auxiliary_tokenizer: Optional[Union[AutoTokenizer, "ExLlamaV2Tokenizer"]] = None # Corrected type hint
_auxiliary_inference_library: Optional[str] = None

# Defines the directory where local models are stored
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# --- Function to discover local model files ---
async def discover_local_models() -> List[ModelFile]:
    """
    Scans the MODELS_DIR for compatible model files and returns a list of ModelFile schemas.
    """
    detected_models: List[ModelFile] = []
    
    # Iterates through all items in MODELS_DIR
    for item_name in os.listdir(MODELS_DIR):
        full_path = os.path.join(MODELS_DIR, item_name)

        # Checks for ExLlamaV2 directories
        if os.path.isdir(full_path) and EXLLAMAV2_AVAILABLE:
            config_path = os.path.join(full_path, "config.json")
            if os.path.exists(config_path) and (glob.glob(os.path.join(full_path, "*.safetensors")) or glob.glob(os.path.join(full_path, "*.bin"))):
                try:
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                    if "exl2_probed_tensor_info" in config_data:
                        size_mb = sum(os.path.getsize(os.path.join(full_path, f)) for f in os.listdir(full_path)) / (1024*1024)
                        detected_models.append(ModelFile(
                            filename=os.path.basename(full_path),
                            path=os.path.relpath(full_path, MODELS_DIR),
                            size_mb=round(size_mb, 2),
                            compatible_libraries=["exllamav2"],
                            suggested_device="cuda",
                            description=f"Quantized model for ExLlamaV2. Size: {round(size_mb, 2)}MB."
                        ))
                except Exception as e:
                    print(f"[DEBUG] Could not parse config for {full_path} as ExLlamaV2: {e}")
        
        # Checks for Transformers-compatible local directories
        if os.path.isdir(full_path):
            if os.path.exists(os.path.join(full_path, "tokenizer.json")) or os.path.exists(os.path.join(full_path, "tokenizer_config.json")):
                if not any(m.path == os.path.relpath(full_path, MODELS_DIR) for m in detected_models):
                    size_mb = sum(os.path.getsize(os.path.join(full_path, f)) for f in os.listdir(full_path)) / (1024*1024)
                    detected_models.append(ModelFile(
                        filename=os.path.basename(full_path) + " (HF Local)",
                        path=os.path.relpath(full_path, MODELS_DIR),
                        size_mb=round(size_mb, 2),
                        compatible_libraries=["transformers"],
                        suggested_device="cpu",
                        description=f"Local Transformers model directory. Size: {round(size_mb, 2)}MB."
                    ))

        # Checks for GGUF files (compatible with both llama_cpp and transformers)
        if os.path.isfile(full_path) and full_path.endswith(".gguf"):
            size_mb = os.path.getsize(full_path) / (1024*1024)
            compatible_libs = []
            if LLAMA_CPP_AVAILABLE:
                compatible_libs.append("llama_cpp")
            compatible_libs.append("transformers")

            if compatible_libs:
                detected_models.append(ModelFile(
                    filename=os.path.basename(full_path),
                    path=os.path.relpath(full_path, MODELS_DIR),
                    size_mb=round(size_mb, 2),
                    compatible_libraries=compatible_libs,
                    suggested_device="cpu",
                    description=f"GGUF model. Size: {round(size_mb, 2)}MB."
                ))

    if hasattr(torch, 'cuda') or hasattr(torch, 'backends'): # Check if torch is loaded at all
        detected_models.append(ModelFile(
            filename="Hugging Face ID (Online)",
            path="Hugging Face ID",
            size_mb=0.0,
            compatible_libraries=["transformers"],
            suggested_device="cpu", # Default, user can change
            description="Load a model directly from Hugging Face Model Hub by ID (e.g., 'gpt2')."
        ))

    return detected_models

async def load_model(
    model_id: str,
    device: Literal["cpu", "cuda", "hip", "vulkan"],
    model_type: Literal["primary", "auxiliary"],
    inference_library: Literal["transformers", "exllamav2", "llama_cpp"],
    max_context: int
):
    """
    Loads an AI model and its tokenizer using the specified inference library.
    """
    global _primary_model, _primary_tokenizer, _primary_inference_library
    global _auxiliary_model, _auxiliary_tokenizer, _auxiliary_inference_library

    try:
        print(f"Attempting to load model '{model_id}' with '{inference_library}' on device '{device}' for type '{model_type}'...")

        model_instance = None
        tokenizer_instance = None
        
        actual_device = "cpu"
        if device == "cuda" and torch.cuda.is_available():
            actual_device = "cuda"
            print("[DEBUG] NVIDIA CUDA detected and selected.")
        elif device == "hip" and hasattr(torch.backends, 'hip') and torch.backends.hip.is_available():
            actual_device = "hip"
            print("[DEBUG] AMD ROCm (HIP) detected and selected.")
        elif device == "vulkan":
            if not LLAMA_CPP_AVAILABLE:
                raise ImportError("llama-cpp-python is not installed or not available for Vulkan.")
            actual_device = "vulkan"
            print("[DEBUG] Vulkan selected for llama.cpp.")
        else:
            if device != "cpu":
                print(f"[WARNING] Requested device '{device}' not available, falling back to CPU.")
            actual_device = "cpu"


        if inference_library == "transformers":
            full_model_path = os.path.join(MODELS_DIR, model_id) if model_id != "Hugging Face ID" else model_id

            if model_id != "Hugging Face ID" and not os.path.exists(full_model_path):
                if full_model_path.endswith(".gguf"):
                    print(f"[DEBUG] Loading GGUF with Transformers: {full_model_path}")
                    tokenizer_instance = AutoTokenizer.from_pretrained(full_model_path, model_max_length=max_context)
                    model_instance = AutoModelForCausalLM.from_pretrained(full_model_path, torch_dtype=torch.float16)
                    model_instance.config.max_position_embeddings = max_context
                else:
                    raise FileNotFoundError(f"Local Transformers model directory/file not found at {full_model_path}")
            else:
                tokenizer_instance = AutoTokenizer.from_pretrained(full_model_path, model_max_length=max_context)
                model_instance = AutoModelForCausalLM.from_pretrained(full_model_path, torch_dtype=torch.float16)
                model_instance.config.max_position_embeddings = max_context
                print(f"[DEBUG] Transformers model loaded from {full_model_path} to {actual_device.upper()}.")

            model_instance.to(actual_device)
            print(f"[DEBUG] Transformers model loaded from {full_model_path} to {actual_device.upper()}.")

        elif inference_library == "exllamav2":
            if not EXLLAMAV2_AVAILABLE:
                raise ImportError("ExLlamaV2 is not installed or not available.")
            if actual_device != "cuda":
                raise ValueError("ExLlamaV2 only supports CUDA devices. Please select CUDA.")
            
            model_path = os.path.join(MODELS_DIR, model_id)
            if not os.path.isdir(model_path):
                raise FileNotFoundError(f"ExLlamaV2 model directory not found at {model_path}")

            config = ExLlamaV2Config()
            config.model_dir = model_path
            config.prepare()
            config.max_seq_len = max_context
            config.max_input_len = max_context 

            tokenizer_instance = ExLlamaV2Tokenizer(config)
            model_instance = ExLlamaV2(config)
            model_instance.load()
            print(f"[DEBUG] ExLlamaV2 model loaded from {model_path} to CUDA.")

        elif inference_library == "llama_cpp":
            if not LLAMA_CPP_AVAILABLE:
                raise ImportError("llama-cpp-python is not installed or not available.")
            
            model_path = os.path.join(MODELS_DIR, model_id)
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"GGUF model file not found at {model_path}")
            
            n_gpu_layers = 0
            if actual_device == "cuda" or actual_device == "hip" or actual_device == "vulkan":
                n_gpu_layers = -1
            
            model_instance = Llama(model_path=model_path, n_gpu_layers=n_gpu_layers, n_ctx=max_context, verbose=False)
            tokenizer_instance = AutoTokenizer.from_pretrained("gpt2")
            print(f"[DEBUG] llama.cpp model loaded from {model_path} with n_gpu_layers={n_gpu_layers}, n_ctx={max_context} (Vulkan/GPU if compiled).")

        else:
            raise ValueError(f"Unknown inference library: {inference_library}")

        if model_type == "primary":
            _primary_model = model_instance
            _primary_tokenizer = tokenizer_instance
            _primary_inference_library = inference_library
        elif model_type == "auxiliary":
            _auxiliary_model = model_instance
            _auxiliary_tokenizer = tokenizer_instance
            _auxiliary_inference_library = inference_library
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        return {"message": f"Model '{model_id}' ({model_type}) loaded successfully with {inference_library}!", "status": "success"}

    except Exception as e:
        print(f"[ERROR] model_manager: Error loading model '{model_id}': {e}")
        return {"message": f"Failed to load model '{model_id}': {str(e)}", "status": "error"}

async def unload_models():
    """
    Unloads all currently loaded primary and auxiliary AI models.
    """
    global _primary_model, _primary_tokenizer, _primary_inference_library
    global _auxiliary_model, _auxiliary_tokenizer, _auxiliary_inference_library

    print("[DEBUG] model_manager: Attempting to unload all models.")
    
    if _primary_model is not None:
        del _primary_model
        del _primary_tokenizer
        _primary_model = None
        _primary_tokenizer = None
        _primary_inference_library = None
        if torch.cuda.is_available() or (torch.backends.vulkan.is_available() if hasattr(torch.backends, 'vulkan') else False): # Clear GPU cache if applicable
            torch.cuda.empty_cache()
        print("[DEBUG] model_manager: Primary model unloaded.")
    
    if _auxiliary_model is not None:
        del _auxiliary_model
        del _auxiliary_tokenizer
        _auxiliary_model = None
        _auxiliary_tokenizer = None
        _auxiliary_inference_library = None
        if torch.cuda.is_available() or (torch.backends.vulkan.is_available() if hasattr(torch.backends, 'vulkan') else False): # Clear GPU cache if applicable
            torch.cuda.empty_cache()
        print("[DEBUG] model_manager: Auxiliary model unloaded.")
    
    print("[DEBUG] model_manager: All models unloaded successfully.")
    return {"message": "All models unloaded successfully!", "status": "success"}


async def generate_text(
    prompt: str,
    max_new_tokens: int,
    temperature: float,
    top_k: int,
    top_p: float,
    model_type: str = "primary",
    selected_character_ids: Optional[List[UUID]] = None,
    selected_plot_point_ids: Optional[List[UUID]] = None
) -> str:
    """
    Generates text using the loaded AI model, incorporating character and plot point context.
    """
    global _primary_model, _primary_tokenizer, _primary_inference_library
    global _auxiliary_model, _auxiliary_tokenizer, _auxiliary_inference_library

    model = _primary_model if model_type == "primary" else _auxiliary_model
    tokenizer = _primary_tokenizer if model_type == "primary" else _auxiliary_tokenizer
    inference_library = _primary_inference_library if model_type == "primary" else _auxiliary_inference_library


    if model is None or tokenizer is None:
        return "Error: AI model not loaded. Please load a model first."

    # Determine the actual device of the loaded model (if applicable)
    model_device = "cpu" # Default
    if inference_library == "transformers" and hasattr(model, 'device'):
        model_device = str(model.device)
    # ExLlamaV2 models are always on CUDA, llama_cpp handles internally

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

    # Combine all context with the main prompt
    full_prompt = character_context + plot_point_context + prompt

    try:
        if inference_library == "transformers":
            inputs = tokenizer(full_prompt, return_tensors="pt").to(model_device)
            output_tokens = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
            generated_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
            
        elif inference_library == "exllamav2":
            if not EXLLAMAV2_AVAILABLE:
                raise RuntimeError("ExLlamaV2 is not available for generation.")
            # ExLlamaV2 generation
            input_ids = tokenizer.encode(full_prompt)
            
            settings = ExLlamaV2Sampler.Settings()
            settings.temperature = temperature
            settings.top_k = top_k
            settings.top_p = top_p
            # Add other ExLlamaV2 specific settings as needed
            
            output_ids = model.generate( # Corrected: use model.generate
                input_ids,
                settings,
                max_new_tokens=max_new_tokens,
                # stop_strings = ["\nUser:", "\n###", "<|im_end|>"] # Example stop strings
            )
            generated_text = tokenizer.decode(output_ids)
            
        elif inference_library == "llama_cpp":
            if not LLAMA_CPP_AVAILABLE:
                raise RuntimeError("llama-cpp-python is not available for generation.")
            # llama.cpp generation
            # The 'prompt' is directly passed to the Llama model's __call__ method
            output = model(
                full_prompt,
                max_tokens=max_new_tokens,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                stop=["\nUser:", "\n###", "<|im_end|>"], # Example stop tokens
                echo=False # Do not echo the prompt back
            )
            generated_text = output["choices"][0]["text"]

        else:
            generated_text = "Error: Unknown inference library for generation."


        # Remove the input prompt from the generated text
        if generated_text.startswith(full_prompt):
            generated_text = generated_text[len(full_prompt):].strip()

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
        model_type="auxiliary",
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