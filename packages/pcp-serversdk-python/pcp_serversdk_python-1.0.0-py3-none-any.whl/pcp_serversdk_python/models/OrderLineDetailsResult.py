from dataclasses import dataclass
from typing import List, Optional

from .CartItemOrderStatus import CartItemOrderStatus
from .OrderLineDetailsInput import OrderLineDetailsInput


@dataclass(kw_only=True)
class OrderLineDetailsResult(OrderLineDetailsInput):
    id: Optional[str] = None
    status: Optional[List[CartItemOrderStatus]] = None
