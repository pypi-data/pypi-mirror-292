import logging

import requests
import tenacity
from requests import Response
from tenacity import stop_after_attempt, wait_exponential

from wapchita.request_wap.headers import get_headers
from wapchita.request_wap.urls import url_get_chat_details

logger = logging.getLogger(__name__)


@tenacity.retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=60))
def get_chat_details(
        *,
        tkn: str,
        device_id: str,
        message_wid: str,
) -> Response:
    url = url_get_chat_details(device_id=device_id, message_wid=message_wid)

    response = requests.get(url=url, headers=get_headers(tkn=tkn))
    if response.status_code >= 500:
        _msg = "Error inesperado de wapchita. Sin causa aparente, se reintenta."
        logger.warning(_msg)
        raise Exception(_msg)
    return response
