from pathlib import Path

import requests
from requests import Response

from wapchita.request_wap.urls import url_upload_file
from wapchita.request_wap.headers import get_headers


def upload_file(*, tkn: str, path_file: Path) -> Response:
    """ TODO: Se pueden cargar varios productos en simultáneo?."""
    url = url_upload_file()
    files = {"file": open(path_file, 'rb')}
    #querystring = {"reference":"optional-reference-id"}
    return requests.post(url=url, files=files, headers=get_headers(tkn=tkn))#, params=querystring)
