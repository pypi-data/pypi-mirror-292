from dataclasses import dataclass
from typing import Optional

from .PayoutOutput import PayoutOutput
from .StatusCategoryValue import StatusCategoryValue
from .StatusValue import StatusValue


@dataclass(kw_only=True)
class PayoutResponse:
    payoutOutput: Optional[PayoutOutput] = None
    status: Optional[StatusValue] = None
    statusCategory: Optional[StatusCategoryValue] = None
    id: Optional[str] = None
