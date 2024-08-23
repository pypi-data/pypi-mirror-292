import requests
from requests import Response

from wapchita.request_wap.headers import get_headers
from wapchita.request_wap.urls import get_url_delete_message


def delete_message(
        *,
        tkn: str,
        message_wid: str = "",
) -> Response:
    url = get_url_delete_message(message_wid=message_wid)
    headers = get_headers(tkn)
    return requests.delete(url, headers=headers)
