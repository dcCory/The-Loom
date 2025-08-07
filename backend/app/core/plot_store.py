from typing import Dict, List, Optional
from uuid import UUID
from app.models.schemas import PlotPoint, PlotPointCreate, PlotPointUpdate

# In-memory store for plot points.
# Key: Plot Point UUID, Value: PlotPoint object
_plot_points: Dict[UUID, PlotPoint] = {}

def create_plot_point(plot_point_data: PlotPointCreate) -> PlotPoint:
    """Creates a new plot point and adds it to the store."""
    new_plot_point = PlotPoint(**plot_point_data.model_dump())
    _plot_points[new_plot_point.id] = new_plot_point
    print(f"Created plot point: {new_plot_point.title} with ID: {new_plot_point.id}")
    return new_plot_point

def get_plot_point(plot_point_id: UUID) -> Optional[PlotPoint]:
    """Retrieves a plot point by its ID."""
    return _plot_points.get(plot_point_id)

def get_all_plot_points() -> List[PlotPoint]:
    """Retrieves all plot points in the store."""
    return list(_plot_points.values())

def update_plot_point(plot_point_id: UUID, update_data: PlotPointUpdate) -> Optional[PlotPoint]:
    """Updates an existing plot point."""
    plot_point = _plot_points.get(plot_point_id)
    if not plot_point:
        return None

    # Updates fields that are provided in update_data
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(plot_point, key, value)
    
    _plot_points[plot_point_id] = plot_point # Ensures updated object is stored
    print(f"Updated plot point with ID: {plot_point_id}")
    return plot_point

def delete_plot_point(plot_point_id: UUID) -> bool:
    """Deletes a plot point by its ID."""
    if plot_point_id in _plot_points:
        del _plot_points[plot_point_id]
        print(f"Deleted plot point with ID: {plot_point_id}")
        return True
    return False