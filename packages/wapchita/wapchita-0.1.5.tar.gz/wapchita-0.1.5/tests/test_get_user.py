from wapchita.client import Wapchita
from wapchita.models.user import WapUser


def test_get_user(wapchita: Wapchita, phone_tester: str) -> None:
    user = wapchita.user_from_phone(phone=phone_tester)
    assert isinstance(user, WapUser) and user.phone == phone_tester
 