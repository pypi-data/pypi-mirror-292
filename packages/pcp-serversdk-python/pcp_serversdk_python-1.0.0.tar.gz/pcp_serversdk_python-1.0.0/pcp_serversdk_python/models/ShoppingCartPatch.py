from dataclasses import dataclass
from typing import List, Optional

from .CartItemPatch import CartItemPatch


@dataclass(kw_only=True)
class ShoppingCartPatch:
    items: Optional[List[CartItemPatch]] = None
