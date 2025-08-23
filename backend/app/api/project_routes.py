from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from app.models.schemas import ProjectCreate, Project, ProjectListItem, ProjectLoadResponse, AvailableProjectsResponse
from app.core import project_manager

router = APIRouter()

@router.get("/available", response_model=AvailableProjectsResponse)
async def get_available_projects():
    """
    Retrieves a list of all available projects (ID and title).
    """
    projects = project_manager.get_available_projects()
    return {"projects": projects}

@router.post("/create", response_model=Project)
async def create_new_project(request: ProjectCreate):
    """
    Creates a new project and sets it as the active project.
    """
    new_project = await project_manager.create_project(request)
    return new_project

@router.post("/load/{project_id}", response_model=ProjectLoadResponse)
async def load_existing_project(project_id: UUID):
    """
    Loads an existing project by ID and sets it as the active project.
    """
    project = await project_manager.load_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    return {"message": f"Project '{project.title}' loaded successfully.", "project": project}

@router.post("/save_active", response_model=ProjectLoadResponse)
async def save_current_active_project():
    """
    Saves the currently active project to disk.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project to save.")
    
    await project_manager.save_active_project()
    return {"message": f"Project '{active_project.title}' saved successfully.", "project": active_project}


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_by_id(project_id: UUID):
    """
    Deletes a project by ID from disk.
    """
    if not await project_manager.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found or could not be deleted.")
    return