from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class WebhookStatus(BaseModel):
   status: str
   webhookSyncedAt: Optional[str]

class WapchitaAudioMeta(BaseModel):
    duration: Optional[int] = None
    hasPreview: bool

class WapchitaAudioStats(BaseModel):
    downloads: int

class WapchitaAudioPreview(BaseModel):
    image: Optional[str] = None

class WapchitaAudioLinks(BaseModel):
    resource: str
    download: str
    chat: str
    contact: str
    message: str

class WapchitaMedia(BaseModel):
    id: str
    message: str
    chat: str
    flow: str                               # Literal["in"] #TODO: Habrá "out"?
    status: str                             # Literal["available"]
    caption: Optional[str] = None
    type: str                               # audio
    size: int
    mime: str                               # audio/mp3
    extension: str                          # mp3
    format: Optional[str | dict] = None     # ptt
    source: Optional[str] = None            # "upload"
    uploadFileId: Optional[str] = None      # Es el ID del elemento subido.
    filename: str
    createdAt: datetime
    expiresAt: datetime
    meta: WapchitaAudioMeta
    stats: WapchitaAudioStats
    preview: WapchitaAudioPreview
    links: WapchitaAudioLinks