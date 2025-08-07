from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from app.models.schemas import PlotPoint, PlotPointCreate, PlotPointUpdate
from app.core import plot_store

router = APIRouter()

@router.post("/", response_model=PlotPoint, status_code=status.HTTP_201_CREATED)
async def create_new_plot_point(plot_point_data: PlotPointCreate):
    """
    Creates a new plot point.
    """
    new_plot_point = plot_store.create_plot_point(plot_point_data)
    return new_plot_point

@router.get("/", response_model=List[PlotPoint])
async def get_all_plot_points():
    """
    Retrieves a list of all plot points.
    """
    return plot_store.get_all_plot_points()

@router.get("/{plot_point_id}", response_model=PlotPoint)
async def get_plot_point_by_id(plot_point_id: UUID):
    """
    Retrieves a single plot point by ID.
    """
    plot_point = plot_store.get_plot_point(plot_point_id)
    if not plot_point:
        raise HTTPException(status_code=404, detail="Plot point not found")
    return plot_point

@router.put("/{plot_point_id}", response_model=PlotPoint)
async def update_existing_plot_point(plot_point_id: UUID, update_data: PlotPointUpdate):
    """
    Updates an existing plot point's details.
    """
    updated_plot_point = plot_store.update_plot_point(plot_point_id, update_data)
    if not updated_plot_point:
        raise HTTPException(status_code=404, detail="Plot point not found")
    return updated_plot_point

@router.delete("/{plot_point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plot_point_by_id(plot_point_id: UUID):
    """
    Deletes a plot point by ID.
    """
    if not plot_store.delete_plot_point(plot_point_id):
        raise HTTPException(status_code=404, detail="Plot point not found")
    return