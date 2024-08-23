from dataclasses import dataclass
from typing import List, Optional

from .CardPaymentDetails import CardPaymentDetails
from .PaymentChannel import PaymentChannel
from .PaymentEvent import PaymentEvent


@dataclass(kw_only=True)
class PaymentInformationResponse:
    commerceCaseId: Optional[str] = None
    checkoutId: Optional[str] = None
    merchantCustomerId: Optional[str] = None
    paymentInformationId: Optional[str] = None
    paymentChannel: Optional[PaymentChannel] = None
    paymentProductId: Optional[int] = None
    terminalId: Optional[str] = None
    cardAcceptorId: Optional[str] = None
    merchantReference: Optional[str] = None
    cardPaymentDetails: Optional[CardPaymentDetails] = None
    events: Optional[List[PaymentEvent]] = None
