import requests
from requests import Response

from wapchita.request_wap.urls import url_edit_message
from wapchita.request_wap.headers import get_headers_app_json


def edit_message(*, tkn: str, device_id: str, message_wid: str, text: str) -> Response:
    """ Tiempo máximo de 20 minutos."""
    url = url_edit_message(device_id=device_id, message_wid=message_wid)
    return requests.patch(url=url, json={"message": text}, headers=get_headers_app_json(tkn=tkn))
