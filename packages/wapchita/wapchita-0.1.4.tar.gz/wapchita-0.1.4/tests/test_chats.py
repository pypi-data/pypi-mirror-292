from constants import WAP_API_KEY, WAP_DEVICE_ID, PHONE_TESTER
from wapchita import Wapchita
from wapchita.utils import phone2wid


def test_get_chats_with_messages():
    wapchita = Wapchita(
        tkn=WAP_API_KEY,
        device=WAP_DEVICE_ID
    )
    chats_response = wapchita.get_chats(user_wid=phone2wid(phone=PHONE_TESTER))
    assert chats_response.status_code == 200
    assert PHONE_TESTER in chats_response.text
    chats = chats_response.json()
    assert isinstance(chats, list)
    assert len(chats) > 0


def test_get_chats_with_wrong_number():
    wapchita = Wapchita(
        tkn=WAP_API_KEY,
        device=WAP_DEVICE_ID
    )
    chats_response = wapchita.get_chats(user_wid=phone2wid(phone='asdasdasd'))
    assert chats_response.status_code == 200
    chats = chats_response.json()
    assert chats == []


def test_get_chats_with_real_message_wid():
    wapchita = Wapchita(
        tkn=WAP_API_KEY,
        device=WAP_DEVICE_ID
    )
    chats_response = wapchita.get_chats(user_wid=phone2wid(phone=PHONE_TESTER),
                                        message_wid='3EB0B89185EF09998F278C')
    assert chats_response.status_code == 200
    assert isinstance(chats_response.json(), list)
    assert len(chats_response.json()) > 0


def test_get_chats_with_wrong_message_wid():
    wapchita = Wapchita(
        tkn=WAP_API_KEY,
        device=WAP_DEVICE_ID
    )
    chats_response = wapchita.get_chats(user_wid=phone2wid(phone=PHONE_TESTER), message_wid='3EB0B89185E9998F278C')
    assert chats_response.status_code in [400, 409]
