from dataclasses import dataclass
from typing import List, Optional

from .CardPaymentMethodSpecificInput import CardPaymentMethodSpecificInput
from .FinancingPaymentMethodSpecificInput import FinancingPaymentMethodSpecificInput
from .MobilePaymentMethodSpecificInput import MobilePaymentMethodSpecificInput
from .PaymentChannel import PaymentChannel
from .PaymentEvent import PaymentEvent
from .RedirectPaymentMethodSpecificInput import RedirectPaymentMethodSpecificInput
from .References import References
from .SepaDirectDebitPaymentMethodSpecificInput import (
    SepaDirectDebitPaymentMethodSpecificInput,
)


@dataclass(kw_only=True)
class PaymentExecution:
    paymentExecutionId: Optional[str] = None
    paymentId: Optional[str] = None
    cardPaymentMethodSpecificInput: Optional[CardPaymentMethodSpecificInput] = None
    mobilePaymentMethodSpecificInput: Optional[MobilePaymentMethodSpecificInput] = None
    redirectPaymentMethodSpecificInput: Optional[RedirectPaymentMethodSpecificInput] = (
        None
    )
    sepaDirectDebitPaymentMethodSpecificInput: Optional[
        SepaDirectDebitPaymentMethodSpecificInput
    ] = None
    financingPaymentMethodSpecificInput: Optional[
        FinancingPaymentMethodSpecificInput
    ] = None
    paymentChannel: Optional[PaymentChannel] = None
    references: Optional[References] = None
    events: Optional[List[PaymentEvent]] = None
