import os
from typing import Optional, List
from uuid import UUID, uuid4
from app.models.schemas import Project, ProjectCreate, Character, CharacterCreate, CharacterUpdate, PlotPoint, PlotPointCreate, PlotPointUpdate, ProjectListItem
from app.core import persistence

_active_project: Optional[Project] = None

def get_active_project() -> Optional[Project]:
    """
    Returns the currently active project.
    """
    return _active_project

def set_active_project(project: Project):
    """
    Sets the provided project as the active project.
    """
    global _active_project
    _active_project = project
    print(f"[DEBUG] project_manager: Active project set to '{project.title}' (ID: {project.id}).")

def clear_active_project():
    """
    Clears the currently active project from memory.
    """
    global _active_project
    _active_project = None
    print("[DEBUG] project_manager: Active project cleared.")

async def create_project(project_data: ProjectCreate) -> Project:
    """
    Creates a new project, saves it to disk, and sets it as active.
    """
    new_project = Project(
        id=uuid4(),
        title=project_data.title,
        story_text="",
        characters=[],
        plot_points=[]
    )
    persistence.save_project(new_project)
    set_active_project(new_project)
    print(f"[DEBUG] project_manager: New project '{new_project.title}' created and set as active.")
    return new_project

async def load_project_by_id(project_id: UUID) -> Optional[Project]:
    """
    Loads a project from disk by its ID and sets it as active.
    """
    project = persistence.load_project(project_id)
    if project:
        set_active_project(project)
        print(f"[DEBUG] project_manager: Project '{project.title}' (ID: {project.id}) loaded and set as active.")
    else:
        print(f"[DEBUG] project_manager: Project ID {project_id} not found.")
    return project

async def save_active_project():
    """
    Saves the currently active project to disk.
    """
    if _active_project:
        persistence.save_project(_active_project)
        print(f"[DEBUG] project_manager: Active project '{_active_project.title}' (ID: {_active_project.id}) saved to disk.")
    else:
        print("[WARNING] project_manager: No active project to save.")

async def delete_project(project_id: UUID) -> bool:
    """
    Deletes a project from disk. If it's the active project, it's cleared from memory.
    """
    if _active_project and _active_project.id == project_id:
        clear_active_project()
        print(f"[DEBUG] project_manager: Active project (ID: {project_id}) cleared from memory due to deletion.")
    
    deleted = persistence.delete_project_file(project_id)
    if deleted:
        print(f"[DEBUG] project_manager: Project ID {project_id} deleted from disk.")
    else:
        print(f"[WARNING] project_manager: Failed to delete project ID {project_id} from disk.")
    return deleted

# Function to get available projects from persistence
def get_available_projects() -> List[ProjectListItem]:
    """
    Retrieves a list of all available projects (ID, title, last_modified) from disk.
    """
    return persistence.get_available_projects()

# --- Character Management for Active Project ---

def get_active_project_characters() -> List[Character]:
    """Returns all characters of the active project."""
    return _active_project.characters if _active_project else []

def get_active_project_character(character_id: UUID) -> Optional[Character]:
    """Returns a specific character from the active project."""
    if _active_project:
        for char in _active_project.characters:
            if char.id == character_id:
                return char
    return None

def add_active_project_character(character_data: CharacterCreate) -> Optional[Character]:
    """Adds a new character to the active project and saves the project."""
    if _active_project:
        new_character = Character(**character_data.model_dump(), id=uuid4())
        _active_project.characters.append(new_character)
        return new_character
    return None

def update_active_project_character(character_id: UUID, update_data: CharacterUpdate) -> Optional[Character]:
    """Updates a character in the active project and saves the project."""
    if _active_project:
        for i, char in enumerate(_active_project.characters):
            if char.id == character_id:
                updated_char_dict = char.model_dump()
                updated_char_dict.update(update_data.model_dump(exclude_unset=True))
                _active_project.characters[i] = Character(**updated_char_dict)
                return _active_project.characters[i]
    return None

def delete_active_project_character(character_id: UUID) -> bool:
    """Deletes a character from the active project and saves the project."""
    if _active_project:
        initial_len = len(_active_project.characters)
        _active_project.characters = [char for char in _active_project.characters if char.id != character_id]
        if len(_active_project.characters) < initial_len:
            return True
    return False

# --- Plot Point Management for Active Project ---

def get_active_project_plot_points() -> List[PlotPoint]:
    """Returns all plot points of the active project."""
    return _active_project.plot_points if _active_project else []

def get_active_project_plot_point(plot_point_id: UUID) -> Optional[PlotPoint]:
    """Returns a specific plot point from the active project."""
    if _active_project:
        for pp in _active_project.plot_points:
            if pp.id == plot_point_id:
                return pp
    return None

def add_active_project_plot_point(plot_point_data: PlotPointCreate) -> Optional[PlotPoint]:
    """Adds a new plot point to the active project and saves the project."""
    if _active_project:
        new_plot_point = PlotPoint(**plot_point_data.model_dump(), id=uuid4())
        _active_project.plot_points.append(new_plot_point)
        return new_plot_point
    return None

def update_active_project_plot_point(plot_point_id: UUID, update_data: PlotPointUpdate) -> Optional[PlotPoint]:
    """Updates a plot point in the active project and saves the project."""
    if _active_project:
        for i, pp in enumerate(_active_project.plot_points):
            if pp.id == plot_point_id:
                updated_pp_dict = pp.model_dump()
                updated_pp_dict.update(update_data.model_dump(exclude_unset=True))
                _active_project.plot_points[i] = PlotPoint(**updated_pp_dict)
                return _active_project.plot_points[i]
    return None

def delete_active_project_plot_point(plot_point_id: UUID) -> bool:
    """Deletes a plot point from the active project and saves the project."""
    if _active_project:
        initial_len = len(_active_project.plot_points)
        _active_project.plot_points = [pp for pp in _active_project.plot_points if pp.id != plot_point_id]
        if len(_active_project.plot_points) < initial_len:
            return True
    return False

# --- Story Text Management for Active Project ---

def get_active_project_story_text() -> str:
    """Returns the story text of the active project."""
    return _active_project.story_text if _active_project else ""

def set_active_project_story_text(text: str):
    """Sets the story text for the active project."""
    if _active_project:
        _active_project.story_text = text