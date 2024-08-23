from dataclasses import dataclass
from typing import Optional

from .PaymentProduct3391SpecificOutput import PaymentProduct3391SpecificOutput


@dataclass(kw_only=True)
class FinancingPaymentMethodSpecificOutput:
    paymentProductId: Optional[int] = None
    paymentProduct3391SpecificOutput: Optional[PaymentProduct3391SpecificOutput] = None
