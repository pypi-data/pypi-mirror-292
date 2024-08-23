from dataclasses import dataclass
from typing import Optional

from .RedirectData import RedirectData


@dataclass(kw_only=True)
class MerchantAction:
    actionType: Optional[str] = None
    redirectData: Optional[RedirectData] = None
