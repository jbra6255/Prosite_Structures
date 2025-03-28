from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Structure:
    structure_id: str
    structure_type: str
    rim_elevation: float
    invert_out_elevation: float
    invert_out_angle: Optional[int] = None  # Optional
    vert_drop: Optional[float] = None       # Made optional
    upstream_structure_id: Optional[str] = None
    pipe_length: Optional[float] = None
    pipe_diameter: Optional[float] = None
    pipe_type: Optional[str] = None
    frame_type: Optional[str] = None
    group_name: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def total_drop(self) -> float:
        """Calculate total drop from frame to invert out"""
        return self.rim_elevation - self.invert_out_elevation

@dataclass
class StructureGroup:
    name: str
    description: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None