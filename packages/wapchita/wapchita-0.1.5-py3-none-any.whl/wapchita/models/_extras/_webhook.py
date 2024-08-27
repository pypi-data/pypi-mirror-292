from typing import Optional, List, Literal
from datetime import datetime

from pydantic import BaseModel, Field

__all__ = [
    "WapData",
    "MsgType",
    "BaseWapMsg",
    "T_TEXT",
    "T_IMAGE",
    "T_STICKER",
    "T_VIDEO",
    "T_LOCATION",
    "T_AUDIO",
    "T_DOCUMENT",
    "T_CONTACTS",
]

T_TEXT = "text"
T_IMAGE = "image"
T_STICKER= "sticker"
T_VIDEO = "video"
T_LOCATION = "location"
T_AUDIO = "audio"
T_DOCUMENT = "document"
T_CONTACTS = "contacts"

MsgType = Literal[
    "text",
    "image",
    "sticker",
    "video",
    "location",
    "audio",
    "document",
    "contacts"
]

class BaseWapMsg(BaseModel):
    @property
    def type(self) -> MsgType: ...      # FIXME: Se está ocultando al usuario.
    @property
    def is_text(self) -> bool: return self.type == T_TEXT
    @property
    def is_image(self) -> bool: return self.type == T_IMAGE
    @property
    def is_sticker(self) -> bool: return self.type == T_STICKER
    @property
    def is_video(self) -> bool: return self.type == T_VIDEO
    @property
    def is_location(self) -> bool: return self.type == T_LOCATION
    @property
    def is_audio(self) -> bool: return self.type == T_AUDIO
    @property
    def is_document(self) -> bool: return self.type == T_DOCUMENT
    @property
    def is_contacts(self) -> bool: return self.type == T_CONTACTS




class WapEvents(BaseModel):
    sent: Optional[dict] = None

class WapLinks(BaseModel):
    message: str
    chat: str
    contact: str
    chatMessages: str
    device: str
    agent: Optional[str] = None

class WapMeta(BaseModel):
    rtl: bool
    containsEmoji: bool
    isGif: bool
    isStar: bool
    isGroup: bool
    isChannel: bool
    isForwarded: bool
    isEphemeral: bool
    isNotification: bool
    isLive: bool
    isBroadcast: bool
    isBizNotification: bool
    isDoc: bool
    isLinkPreview: bool
    isPSA: bool
    isRevoked: bool
    isUnreadType: bool
    isFailed: bool
    notifyName: str
    source: str
    via: Optional[str] = None
    isFirstMessage: Optional[bool] = None

class WapStats(BaseModel):
    notes: int
    localMessages: int
    inboundMessages: int
    outboundMessages: int

class WapOwner(BaseModel):
    agent: Optional[str]
    assigner: Optional[str] = None
    assignedAt: Optional[str] = None

class WapChat(BaseModel):
    id: str
    name: Optional[str] = None
    date: Optional[str] = None
    type: Literal["chat", "group"]
    status: str
    waStatus: str
    statusUpdatedAt: Optional[str] = None
    firstMessageAt: str
    lastMessageAt: str
    lastOutboundMessageAt: Optional[str] = None
    lastInboundMessageAt: Optional[str] = None
    lastAutoReply: None                 # ---> TODO
    lastAutoReplyAt: None               # ---> TODO
    stats: WapStats
    labels: List[str]
    owner: WapOwner
    contact: dict                       # ---> TODO
    links: dict                         # ---> TODO

    @property
    def is_chat(self) -> bool:
        return self.type == "chat"
    
    @property
    def is_group(self) -> bool:
        return self.type == "group"


class WapData(BaseWapMsg):
    id: str
    type: MsgType
    flow: str
    status: str
    ack: str
    agent: Optional[str] = None
    from_: str = Field(alias="from")
    fromNumber: str
    to: str
    toNumber: str
    date: datetime
    timestamp: int
    body: Optional[str] = None
    chat: WapChat
    events: WapEvents
    meta: WapMeta
    links: WapLinks
