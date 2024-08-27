import requests
from requests import Response

from wapchita.request_wap.urls import url_search_chats
from wapchita.request_wap.headers import get_headers


def search_chat(*, tkn: str, phone: str, device_id: str) -> Response:
    """
    - TODO: Ver search_chats en plural.
    - TODO: Ver si se puede filtrar por fecha, diferencia de tiempo entre mensajes, algo asi.
    - https://app.shock.uy/docs/#tag/Chats/operation/getDeviceChats
    """
    url = url_search_chats(device_id=device_id)
    return requests.get(url=url, headers=get_headers(tkn=tkn), params={"phone": phone})
