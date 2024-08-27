import requests
from requests import Response

from wapchita.typings import Priority, PRIORITY_DEFAULT
from wapchita.request_wap.urls import url_send_message
from wapchita.request_wap.headers import get_headers_app_json


def send_message(
        *,
        tkn: str,
        phone: str,
        message: str = "",
        file_id: str = None,
        priority: Priority = PRIORITY_DEFAULT
    ) -> Response:
    url = url_send_message()
    json_ = {"phone": phone, "message": message, "priority": priority}
    if file_id is not None:
        json_["media"] = {"file": file_id}
    return requests.post(url=url, json=json_, headers=get_headers_app_json(tkn=tkn))
