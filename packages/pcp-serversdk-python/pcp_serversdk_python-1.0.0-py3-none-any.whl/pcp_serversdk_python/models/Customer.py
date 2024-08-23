from dataclasses import dataclass
from typing import Optional

from .Address import Address
from .CompanyInformation import CompanyInformation
from .ContactDetails import ContactDetails
from .PersonalInformation import PersonalInformation


@dataclass(kw_only=True)
class Customer:
    companyInformation: Optional[CompanyInformation] = None
    merchantCustomerId: Optional[str] = None
    billingAddress: Optional[Address] = None
    contactDetails: Optional[ContactDetails] = None
    fiscalNumber: Optional[str] = None
    businessRelation: Optional[str] = None
    locale: Optional[str] = None
    personalInformation: Optional[PersonalInformation] = None
