from pathlib import Path

from wapchita.models.device import WapDevice
from wapchita.request_wap._basics._device_by_id import device_by_id


def phone2wid(*, phone: str) -> str:
    """ TODO: Verificar si todos los `wid` terminan en @c.us"""
    return f"{phone.lstrip('+')}@c.us"

def instance_device(tkn: str, device: WapDevice | str | Path) -> WapDevice:
    if isinstance(device, WapDevice):
        pass
    elif isinstance(device, str):
        device = WapDevice(**device_by_id(tkn=tkn, device_id=device).json())
    elif isinstance(device, Path):
        raise NotImplementedError("No implementado.")
    else:
        raise Exception("Valor inválido para instancia el device.")
    return device
