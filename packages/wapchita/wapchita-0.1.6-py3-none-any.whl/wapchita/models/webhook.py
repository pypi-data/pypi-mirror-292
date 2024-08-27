from typing import List

from wapchita.models.device import WapDevice
from wapchita.models._extras._webhook import WapData, BaseWapMsg, MsgType

__all__ = ["WapWebhookBody", "WapData", "BaseWapMsg", "MsgType"]


class WapWebhookBody(BaseWapMsg):
    id: str
    object: str
    event: str
    created: int
    device: WapDevice
    data: WapData

    @property
    def type(self) -> MsgType:
        return self.data.type

    @property
    def message_wid(self) -> str:
        return self.id

    @property
    def text(self) -> str | None:
        return self.data.body

    @property
    def labels(self) -> List[str]:
        """ Etiquetas configurables del lado de Wapchita."""
        return self.data.chat.labels
    
    @property
    def device_id(self) -> str:
        return self.device.id
    
    @property
    def device_phone(self) -> str:
        return self.device.phone
    
    @property
    def from_phone(self) -> str:
        return self.data.fromNumber
    
    @property
    def to_phone(self) -> str:
        return self.data.toNumber

    #----------Categoría del Mensaje----------
    @property
    def is_bot_request(self) -> bool:
        """ Retorna True la solicitud viene del propio bot."""
        return self.device_phone == self.from_phone

    @property
    def is_chat(self) -> bool:
        return self.data.chat.is_chat

    @property
    def is_group(self) -> bool:
        return self.data.chat.is_group
