from wapchita.client import Wapchita


def test_send_message_text(wapchita: Wapchita, phone_tester: str, text_test: str) -> None:
    r = wapchita.send_message(phone=phone_tester, message=text_test)
    assert r.status_code == 201
