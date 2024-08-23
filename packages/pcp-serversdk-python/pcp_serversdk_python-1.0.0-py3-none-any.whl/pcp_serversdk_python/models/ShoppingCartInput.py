from dataclasses import dataclass
from typing import List, Optional

from .CartItemInput import CartItemInput


@dataclass(kw_only=True)
class ShoppingCartInput:
    items: Optional[List[CartItemInput]] = None
