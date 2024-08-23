from dataclasses import dataclass
from typing import List, Optional

from .ReturnItem import ReturnItem
from .ReturnType import ReturnType


@dataclass(kw_only=True)
class ReturnRequest:
    returnType: Optional[ReturnType] = None
    returnReason: Optional[str] = None
    returnItems: Optional[List[ReturnItem]] = None
