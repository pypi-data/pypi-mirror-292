from dataclasses import dataclass
from typing import List, Optional

from .CartItemInput import CartItemInput


@dataclass(kw_only=True)
class ReturnInformation:
    returnReason: Optional[str] = None
    items: Optional[List[CartItemInput]] = None
