from dataclasses import dataclass
from typing import List, Optional

from .InstallmentOption import InstallmentOption


@dataclass(kw_only=True)
class PaymentProduct3391SpecificOutput:
    installmentOptions: Optional[List[InstallmentOption]] = None
