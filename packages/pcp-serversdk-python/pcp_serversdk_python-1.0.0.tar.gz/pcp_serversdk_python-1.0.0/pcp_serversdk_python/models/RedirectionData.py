from dataclasses import dataclass


@dataclass(kw_only=True)
class RedirectionData:
    returnUrl: str
