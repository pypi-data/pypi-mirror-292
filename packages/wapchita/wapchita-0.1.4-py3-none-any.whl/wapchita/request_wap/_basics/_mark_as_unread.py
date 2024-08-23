import requests
from requests import Response

from wapchita.request_wap.headers import get_headers_app_json
from wapchita.request_wap.urls import url_mark_as_unread


def mark_as_unread(
        *,
        tkn: str,
        device_id: str,
        user_wid: str,
        unread: bool = True
) -> Response:
    url = url_mark_as_unread(device_id=device_id, user_wid=user_wid)
    payload = {"unread": unread}
    return requests.patch(url, json=payload, headers=get_headers_app_json(tkn=tkn))
