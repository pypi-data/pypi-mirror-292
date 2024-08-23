from dataclasses import dataclass
from typing import Optional

from .ProductType import ProductType


@dataclass(kw_only=True)
class OrderLineDetailsInput:
    productCode: Optional[str] = None
    productPrice: int
    productType: Optional[ProductType] = None
    quantity: int
    taxAmount: Optional[int] = None
    productUrl: Optional[str] = None
    productImageUrl: Optional[str] = None
    productCategoryPath: Optional[str] = None
    merchantShopDeliveryReference: Optional[str] = None
