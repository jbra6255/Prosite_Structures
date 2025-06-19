from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Structure:
    structure_id: str  
    structure_type: str
    rim_elevation: float
    invert_out_elevation: float
    run_designation: str = "A"  
    invert_out_angle: Optional[int] = None  
    vert_drop: Optional[float] = None       
    upstream_structure_id: Optional[str] = None
    upstream_run_designation: Optional[str] = None  
    pipe_length: Optional[float] = None
    pipe_diameter: Optional[float] = None
    pipe_type: Optional[str] = None
    frame_type: Optional[str] = None
    description: Optional[str] = None
    group_name: Optional[str] = None
    is_primary_run: bool = True  
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def display_id(self) -> str:
        """Get display ID for the treeview (shows run designation)"""
        if self.run_designation and self.run_designation != "A":
            return f"{self.structure_id}-{self.run_designation}"
        return self.structure_id

    @property
    def upstream_display_id(self) -> Optional[str]:
        """Get upstream display ID including run designation"""
        if not self.upstream_structure_id:
            return None
        if self.upstream_run_designation and self.upstream_run_designation != "A":
            return f"{self.upstream_structure_id}-{self.upstream_run_designation}"
        return self.upstream_structure_id

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

@dataclass
class StructureComponent:
    structure_id: str
    component_type_id: int
    status: str
    project_id: Optional[int] = None
    id: Optional[int] = None
    component_type_name: Optional[str] = None
    order_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class ComponentType:
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class StructureRun:
    """Represents a pipe run between two structure runs"""
    id: Optional[int] = None
    upstream_structure_id: str = ""
    upstream_run_designation: str = "A"
    downstream_structure_id: str = ""
    downstream_run_designation: str = "A"
    pipe_length: Optional[float] = None
    pipe_diameter: Optional[float] = None
    pipe_type: Optional[str] = None
    slope: Optional[float] = None
    project_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def run_name(self) -> str:
        """Generate a name for this run"""
        upstream = f"{self.upstream_structure_id}-{self.upstream_run_designation}"
        downstream = f"{self.downstream_structure_id}-{self.downstream_run_designation}"
        return f"{upstream} → {downstream}"
