from dataclasses import dataclass


@dataclass(kw_only=True)
class BankAccountInformation:
    iban: str
    accountHolder: str
