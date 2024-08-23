from dataclasses import dataclass
from typing import List, Optional

from .OrderItem import OrderItem
from .OrderType import OrderType
from .PaymentMethodSpecificInput import PaymentMethodSpecificInput
from .References import References


@dataclass(kw_only=True)
class OrderRequest:
    orderType: Optional[OrderType] = None
    orderReferences: Optional[References] = None
    items: Optional[List[OrderItem]] = None
    paymentMethodSpecificInput: Optional[PaymentMethodSpecificInput] = None
