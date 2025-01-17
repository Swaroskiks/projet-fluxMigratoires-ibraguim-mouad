from dataclasses import dataclass
from typing import Optional

@dataclass
class AppState:
    selected_species: Optional[str] = None
    view_mode: str = "scatter"
    time_index: int = 0

state = AppState()