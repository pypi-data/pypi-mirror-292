import requests
from requests import Response

from wapchita.request_wap.headers import get_headers
from wapchita.request_wap.urls import url_download_file


def download_file(*, tkn: str, device_id: str, file_id: str) -> Response:
    """ https://app.shock.uy/docs/#tag/Chat-Files/operation/downloadDeviceFileDetails"""
    url = url_download_file(device_id=device_id, file_id=file_id)
    return requests.get(url=url, headers=get_headers(tkn=tkn))
