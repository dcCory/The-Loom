from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from app.models.schemas import PlotPoint, PlotPointCreate, PlotPointUpdate
from app.core import project_manager

router = APIRouter()

@router.post("/", response_model=PlotPoint, status_code=status.HTTP_201_CREATED)
async def create_new_plot_point(plot_point_data: PlotPointCreate):
    """
    Creates a new plot point for the active project.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Please load or create a project first.")
    
    new_plot_point = project_manager.add_active_project_plot_point(plot_point_data)
    if not new_plot_point:
        raise HTTPException(status_code=500, detail="Failed to add plot point to active project.")
    
    await project_manager.save_active_project()
    return new_plot_point

@router.get("/", response_model=List[PlotPoint])
async def get_all_plot_points():
    """
    Retrieves a list of all plot points in the active project.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        return []
    
    return project_manager.get_active_project_plot_points()

@router.get("/{plot_point_id}", response_model=PlotPoint)
async def get_plot_point_by_id(plot_point_id: UUID):
    """
    Retrieves a single plot point by ID from the active project.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Cannot retrieve plot point.")
    
    plot_point = project_manager.get_active_project_plot_point(plot_point_id)
    if not plot_point:
        raise HTTPException(status_code=404, detail="Plot point not found in active project.")
    return plot_point

@router.put("/{plot_point_id}", response_model=PlotPoint)
async def update_existing_plot_point(plot_point_id: UUID, update_data: PlotPointUpdate):
    """
    Updates an existing plot point's details in the active project.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Cannot update plot point.")
    
    updated_plot_point = project_manager.update_active_project_plot_point(plot_point_id, update_data)
    if not updated_plot_point:
        raise HTTPException(status_code=404, detail="Plot point not found in active project.")
    
    await project_manager.save_active_project()
    return updated_plot_point

@router.delete("/{plot_point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plot_point_by_id(plot_point_id: UUID):
    """
    Deletes a plot point by ID from the active project.
    """
    active_project = project_manager.get_active_project()
    if not active_project:
        raise HTTPException(status_code=400, detail="No active project. Cannot delete plot point.")
    
    if not project_manager.delete_active_project_plot_point(plot_point_id):
        raise HTTPException(status_code=404, detail="Plot point not found in active project.")
    
    await project_manager.save_active_project()
    return