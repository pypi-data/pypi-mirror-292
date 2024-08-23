from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class CardFraudResults:
    avsResult: Optional[str] = None
