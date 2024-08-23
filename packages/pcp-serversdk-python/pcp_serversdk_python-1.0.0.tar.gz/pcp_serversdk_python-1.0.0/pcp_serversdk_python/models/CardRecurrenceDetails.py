from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class CardRecurrenceDetails:
    recurringPaymentSequenceIndicator: Optional[str] = None
