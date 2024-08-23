from dataclasses import dataclass
from typing import List, Optional

from .APIError import APIError


@dataclass(kw_only=True)
class ErrorResponse:
    errorId: Optional[str] = None
    errors: Optional[List[APIError]] = None
