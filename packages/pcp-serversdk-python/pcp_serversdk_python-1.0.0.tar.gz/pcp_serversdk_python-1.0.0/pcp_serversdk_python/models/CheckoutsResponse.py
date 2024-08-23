from dataclasses import dataclass
from typing import List

from .CheckoutResponse import CheckoutResponse


@dataclass(kw_only=True)
class CheckoutsResponse:
    numberOfCheckouts: int
    checkouts: List[CheckoutResponse]
