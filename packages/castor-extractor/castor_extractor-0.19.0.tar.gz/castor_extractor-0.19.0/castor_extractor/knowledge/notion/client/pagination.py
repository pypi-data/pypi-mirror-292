from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class PaginatedResponse:
    """Class to handle paginated results"""

    results: list
    next_cursor: Optional[str]
    has_more: bool

    @property
    def start_cursor(self) -> dict:
        return {"start_cursor": self.next_cursor}
