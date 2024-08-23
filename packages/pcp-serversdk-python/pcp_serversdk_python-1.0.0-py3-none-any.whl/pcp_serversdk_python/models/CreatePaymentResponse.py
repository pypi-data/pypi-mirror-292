from dataclasses import dataclass
from typing import Optional

from .MerchantAction import MerchantAction
from .PaymentCreationOutput import PaymentCreationOutput
from .PaymentResponse import PaymentResponse


@dataclass(kw_only=True)
class CreatePaymentResponse:
    creationOutput: Optional[PaymentCreationOutput] = None
    merchantAction: Optional[MerchantAction] = None
    payment: Optional[PaymentResponse] = None
    paymentExecutionId: Optional[str] = None
