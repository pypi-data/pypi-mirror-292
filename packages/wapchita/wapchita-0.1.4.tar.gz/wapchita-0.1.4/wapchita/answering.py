from typing import Literal

from pydantic import BaseModel

#- type='simple': Envía el mensaje en cuanto lo tenga.
#- type='blocks': Itera sobre el mensaje completo para generar la respuesta.
#- TODO: type='stream': Itera sobre el stream de datos para generar la respuesta.
class HowAnswer(BaseModel):
    type: Literal["simple", "blocks", "stream"]

DEFAULT_ANSWER_SIMPLE = "simple"
DEFAULT_ANSWER_BLOCKS = "blocks"
DEFAULT_ANSWER_STREAM = "stream"

class Answering:
    def __init__(self, *, how_answer: HowAnswer):
        self.how_answer = how_answer

    def handle_answer_type(self, *, answer_type: str) -> None:
        pass

    def answer_simple(self):
        pass


# if self.cfg.method_show == "blocks":
#     # Mensaje de espera mientras se procesa la solicitud.
#     r = self.tool_kit.wapchita.send_message(phone=user.phone, message=random_wait_msg())
#     if r.status_code != 201:
#         raise Exception("Error al enviar primer mensaje aleatorio.")
#     msg_response_wid = r.json()["waId"]
#     logger.info(f"msg_response_wid: {msg_response_wid}")

# logger.debug("- Enviando mensaje")
# # msg_response_wid -> Editar. Ver si pueden convivir las 2 versiones, manda mensaje de una o edita.
# if self.cfg.method_show == METHOD_SHOW_SIMPLE:
#     self.tool_kit.wapchita.send_message(phone=user.phone, message=content)
# elif self.cfg.method_show == METHOD_SHOW_BLOCKS:
#     answer_blocks(content=content, msg_response_wid=msg_response_wid, wapchita=self.tool_kit.wapchita)
# elif self.cfg.method_show == METHOD_SHOW_STREAM:
#     raise NotImplementedError("Stream de datos no implementado, volver función async.")
# else:
#     raise ValueError("Valor inválido.")
