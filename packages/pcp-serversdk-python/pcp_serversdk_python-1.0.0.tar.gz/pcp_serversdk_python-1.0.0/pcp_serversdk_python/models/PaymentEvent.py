from dataclasses import dataclass
from typing import Optional

from .AmountOfMoney import AmountOfMoney
from .CancellationReason import CancellationReason
from .PaymentType import PaymentType
from .StatusValue import StatusValue


@dataclass(kw_only=True)
class PaymentEvent:
    type: Optional[PaymentType] = None
    amountOfMoney: Optional[AmountOfMoney] = None
    paymentStatus: Optional[StatusValue] = None
    cancellationReason: Optional[CancellationReason] = None
    returnReason: Optional[str] = None
