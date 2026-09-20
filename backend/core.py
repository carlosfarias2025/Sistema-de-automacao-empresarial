import yagmail
import os
import threading
from dotenv import load_dotenv
from Database import database
from msg_core import CaixaDeMensagens, Mensagem

load_dotenv()
email = os.getenv('EMAIL_USER')
password = os.getenv('EMAIL_PASS')
yag = yagmail.SMTP(email, password)

automations = database.all("automations","nome",all=True)


class Core(threading.Thread):
    def __init__(self,msg:CaixaDeMensagens):
        super().__init__()
        self.msg = msg
        self.name = "core"

    def run(self):
            self.msg.enviar(Mensagem(
                de=self.name,
                para="api",
                tipo="teste",
                dados = {}
            ))
