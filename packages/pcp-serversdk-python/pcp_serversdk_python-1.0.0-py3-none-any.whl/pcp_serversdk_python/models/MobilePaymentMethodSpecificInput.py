from dataclasses import dataclass
from typing import Optional

from .AuthorizationMode import AuthorizationMode
from .PaymentProduct320SpecificInput import PaymentProduct320SpecificInput


@dataclass(kw_only=True)
class MobilePaymentMethodSpecificInput:
    paymentProductId: Optional[int] = None
    authorizationMode: Optional[AuthorizationMode] = None
    encryptedPaymentData: Optional[str] = None
    publicKeyHash: Optional[str] = None
    ephemeralKey: Optional[str] = None
    paymentProduct302SpecificInput: Optional[PaymentProduct320SpecificInput] = None
