"""
- FIXME: Realmente no necesito el device, solo su ID y el número, pero
quizás otros datos como el nombre y demás puedan ayudarme en el futuro.
"""
from pathlib import Path
from typing import List, Optional, TypeVar

import httpx
from requests import Response

from wapchita.async_tools import run_parallel
from wapchita.models.chats import WapChat
from wapchita.models.device import WapDevice
from wapchita.models.user import WapUser
from wapchita.request_wap.request_wap import RequestWap
from wapchita.request_wap.utils import wait_msg_sent, async_wait_msg_sent
from wapchita.typings import Priority, PRIORITY_DEFAULT, SortChats, SORTCHATS_DEFAULT

# from wapchita.answering import Answering


T_Wapchita = TypeVar("T_Wapchita", bound="Wapchita")


class Wapchita:
    def __init__(self, *, tkn: str, device: WapDevice | str | Path):
        self._request_wap = RequestWap(tkn=tkn, device=device)
        # self._answering = Answering()

    @property
    def request_wap(self) -> RequestWap:
        return self._request_wap

    @property
    def device(self) -> WapDevice:
        return self.request_wap.device

    @property
    def device_id(self) -> WapDevice:
        return self.request_wap.device.id

    def user_from_phone(self, *, phone: str, create_if_404: bool = False) -> WapUser:
        r = self.request_wap.contacts(phone=phone, create_if_404=create_if_404)
        if r.status_code != 200:
            raise Exception(f"Error al buscar usuario, documentar. {r.json()}")
        return WapUser(**self.request_wap.contacts(phone=phone).json())

    def create_contact(self, *, phone: str, name: Optional[str] = None, surname: Optional[str] = None) -> Response:
        return self.request_wap.create_contact(phone=phone, name=name, surname=surname)

    def send_message(self, *, phone: str, message: str = "", file_id: str = None,
                     priority: Priority = PRIORITY_DEFAULT) -> Response:
        return self.request_wap.send_message(phone=phone, message=message, file_id=file_id, priority=priority)

    def edit_message(self, *, message_wid: str, text: str) -> Response:
        return self.request_wap.edit_message(message_wid=message_wid, text=text)

    def get_chats(self, *, user_wid: str, sort_: SortChats = SORTCHATS_DEFAULT,
                  message_wid: Optional[str] = None) -> Response:
        return self.request_wap.get_chats(user_wid=user_wid, sort_=sort_, message_wid=message_wid)

    async def async_get_chats(self, *, user_wid: str, sort_: SortChats = SORTCHATS_DEFAULT,
                              message_wid: Optional[str] = None) -> Response:
        return self.request_wap.get_chats(user_wid=user_wid, sort_=sort_, message_wid=message_wid)

    async def async_get_chat_details(self, *, message_wid: str) -> Response:
        return self.request_wap.get_chat_details(message_wid=message_wid)

    async def async_get_chats_history(self, *, user_wid: str, message_wid: str) -> List[WapChat]:
        chats_before, chat_current = await run_parallel(*[
            self.async_get_chats(user_wid=user_wid, message_wid=message_wid),
            self.async_get_chat_details(message_wid=message_wid)
        ])
        # TODO control de status 200
        history = chats_before.json()
        history.reverse()
        history.append(chat_current.json())
        return [WapChat(**chat) for chat in history]

    def download_file(self, *, file_id: str) -> Response:
        return self.request_wap.download_file(file_id=file_id)

    def upload_file(self, *, path_file: Path) -> Response:
        return self.request_wap.upload_file(path_file=path_file)

    def update_chat_labels(self, *, user_wid: str, labels: List[str] = None) -> Response:
        return self.request_wap.update_chat_labels(user_wid=user_wid, labels=labels)

    def upload_send_img(self, *, path_img: Path, phone: str) -> str:
        response_upload = self.upload_file(path_file=path_img)
        try:  # FIXME: Si el fichero existe tira un 400, por que te dice que uses el existente, y retorna el file_id.
            file_id = response_upload.json()[0]["id"]
        except Exception as e:
            file_id = response_upload.json()["meta"]["file"]
        self.send_message(phone=phone, file_id=file_id)
        return file_id

    def mark_as_unread(self, *, user_wid: str, unread: bool = True) -> Response:
        return self.request_wap.mark_as_unread(user_wid=user_wid, unread=unread)

    def delete_message(self, *, message_wid: str) -> Response:
        return self.request_wap.delete_message(message_wid=message_wid)

    def wait_msg_sent(self, *, message_wid: str) -> Response:
        return wait_msg_sent(tkn=self._request_wap.tkn, message_wid=message_wid)

    async def async_wait_msg_sent(self, *, message_wid: str) -> httpx.Response:
        return await async_wait_msg_sent(tkn=self._request_wap.tkn, message_wid=message_wid)
