from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class RedirectPaymentProduct840SpecificInput:
    addressSelectionAtPayPal: Optional[bool] = False
