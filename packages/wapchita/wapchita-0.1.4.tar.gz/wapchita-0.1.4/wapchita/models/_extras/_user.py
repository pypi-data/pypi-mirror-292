from typing import List, Optional

from pydantic import BaseModel

__all__ = ["WapUserLocInfo", "WapMetaUser"]


class WapLang(BaseModel):
    code: str
    iso: str
    name: str
    nativeName: str

class WapUserLocInfo(BaseModel):
    alpha2: str     # TODO: Usar alpha2 y alpha3 como Literal.
    alpha3: str     # TODO: Usar alpha2 y alpha3 como Literal.
    countryCallingCodes: List[str]
    currencies: List[str]
    emoji: str
    ioc: str
    languages: List[WapLang]
    name: str
    status: str     # TODO: Es Literal?

class WapMetaUser(BaseModel):
        isBusiness: bool
        isContact: bool
        isContactBlocked: bool
        isDetachedContact: bool
        isEnterprise: bool
        isGroupParticipant: Optional[bool] = None
        isPSA: bool
        isVerified: bool
        isWAContact: bool
        plaintextDisabled: bool
        showBusinessCheckmark: bool
        statusMute: bool
