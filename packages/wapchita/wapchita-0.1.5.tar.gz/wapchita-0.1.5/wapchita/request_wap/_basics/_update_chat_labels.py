from typing import List, Optional

import requests
from requests import Response

from wapchita.request_wap.urls import url_update_chat_labels
from wapchita.request_wap.headers import get_headers_app_json


def update_chat_labels(
        *,
        tkn: str,
        device_id: str,
        user_wid: str,
        labels: Optional[List[str]] = None
    ) -> Response:
    url = url_update_chat_labels(device_id=device_id, user_wid=user_wid)
    if labels is None:
        labels = []
    return requests.patch(url=url, json=labels, headers=get_headers_app_json(tkn=tkn))
