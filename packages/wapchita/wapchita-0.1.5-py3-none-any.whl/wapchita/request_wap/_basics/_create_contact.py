from typing import Optional

import requests
from requests import Response

from wapchita.request_wap.headers import get_headers_app_json
from wapchita.request_wap.urls import url_create_contact

def create_contact(*, tkn: str, device_id: str, phone: str, name: Optional[str] = None, surname: Optional[str] = None) -> Response:
    """ TODO: Mejorar input con payload o algo asi con pydantic.
    - https://app.shock.uy/docs/#tag/Chat-Contacts/operation/createContact
    - 200 es ok.
    - Si tira 409 es que ya existe el contacto.
    """
    url = url_create_contact(device_id=device_id)
    payload = {"phone": phone}
    if name is not None:
        payload["name"] = name
    if surname is not None:
        payload["surname"] = surname
    return requests.post(url, json=payload, headers=get_headers_app_json(tkn=tkn))

#payload = {
#    "name": f"{o.comprador.apellido}, {o.comprador.nombre}",
#    #"surname": "Doe",
#    #"kind": "personal",
#    #"email": "john@domain.com",
#    "phone": o.comprador.telefono,
#    #"country": "US",
#    #"city": "Ney York",
#    #"postalCode": "12345",
#    #"metadata": [
#    #    {
#    #        "key": "CRM_ID",
#    #        "value": "12345678"
#    #    }
#    #]
#}
