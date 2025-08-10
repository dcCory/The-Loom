from typing import Dict, List, Optional
from uuid import UUID
from app.models.schemas import PlotPoint, PlotPointCreate, PlotPointUpdate
from app.core import persistence

# In-memory store for plot points.
# Key: Plot Point UUID, Value: PlotPoint object
_plot_points: Dict[UUID, PlotPoint] = persistence.load_plot_points()
print(f"[DEBUG] plot_store: Initial load, _plot_points has {len(_plot_points)} entries.") # DEBUG PRINT

def create_plot_point(plot_point_data: PlotPointCreate) -> PlotPoint:
    print(f"[DEBUG] plot_store: Before creating {plot_point_data.title}, _plot_points has {len(_plot_points)} entries.") # DEBUG PRINT
    """Creates a new plot point and adds it to the store."""
    new_plot_point = PlotPoint(**plot_point_data.model_dump())
    _plot_points[new_plot_point.id] = new_plot_point
    print(f"[DEBUG] plot_store: After creating {new_plot_point.title}, _plot_points has {len(_plot_points)} entries. Saving...") # DEBUG PRINT
    persistence.save_plot_points(_plot_points) # Saves after creation
    print(f"[DEBUG] plot_store: Saved plot points after creating {new_plot_point.title}.") # DEBUG PRINT
    return new_plot_point

def get_plot_point(plot_point_id: UUID) -> Optional[PlotPoint]:
    """Retrieves a plot point by its ID."""
    return _plot_points.get(plot_point_id)

def get_all_plot_points() -> List[PlotPoint]:
    print(f"[DEBUG] plot_store: get_all_plot_points called, returning {len(_plot_points)} entries.") # DEBUG PRINT
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
    persistence.save_plot_points(_plot_points) # Saves after update
    print(f"[DEBUG] plot_store: Saved plot points after updating {plot_point_id}.") # DEBUG PRINT
    return plot_point

def delete_plot_point(plot_point_id: UUID) -> bool:
    """Deletes a plot point by its ID."""
    if plot_point_id in _plot_points:
        del _plot_points[plot_point_id]
        persistence.save_plot_points(_plot_points) # Saves after deletion
        print(f"[DEBUG] plot_store: Saved plot points after deleting {plot_point_id}.") # DEBUG PRINT
        return True
    return False