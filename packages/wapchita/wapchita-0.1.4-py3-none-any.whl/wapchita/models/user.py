from typing import TypeVar, Literal, Optional, Any
from datetime import datetime

from pydantic import BaseModel

from wapchita.models._extras._user import WapUserLocInfo, WapMetaUser
from wapchita.models.device import WapDevice

__all__ = ["WapUser"]

T_WapUser = TypeVar("T_WapUser", bound="WapUser")

class WapUser(BaseModel):
    wid: str                        # TODO: Revisar que phone2wid() == wid
    phone: str
    type: Literal["user"]
    displayName: Optional[str] = None
    shortName: Optional[str] = None
    syncedAt: datetime
    createdBy: Optional[Any]        # TODO: Ver.
    locationInfo: WapUserLocInfo
    info: dict
    meta: WapMetaUser
    metadata: list
    device: WapDevice

