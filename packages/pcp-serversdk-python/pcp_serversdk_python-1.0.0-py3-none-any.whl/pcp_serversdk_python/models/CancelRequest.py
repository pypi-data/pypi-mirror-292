from dataclasses import dataclass
from typing import List, Optional

from .CancelItem import CancelItem
from .CancellationReason import CancellationReason
from .CancelType import CancelType


@dataclass(kw_only=True)
class CancelRequest:
    cancelType: Optional[CancelType] = None
    cancellationReason: Optional[CancellationReason] = None
    cancelItems: Optional[List[CancelItem]] = None
