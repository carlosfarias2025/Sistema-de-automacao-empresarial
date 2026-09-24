import yagmail
import os
import threading
from dotenv import load_dotenv
from Database import database
from msg_core import CaixaDeMensagens, Mensagem
import time
import logging

load_dotenv()
email = os.getenv('EMAIL_USER')
password = os.getenv('EMAIL_PASS')
enviar = os.getenv('ENVIAR')
yag = yagmail.SMTP(email, password)

automations = database.all("automations","nome",all=True)
log = logging.getLogger("CORE")
log.setLevel(logging.INFO)
log.propagate = False

formatter = logging.Formatter('%(name)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
log.addHandler(console_handler)

class Core(threading.Thread):
    def __init__(self,msg:CaixaDeMensagens):
        super().__init__()
        self.msg = msg
        self.name = "core"
        self.valores = []

        for i in automations:
            self.valores.append(i.nome)

        log.info("Core iniciado")

    def run(self):
        while True:
            receber = self.msg.receber(self.name)

            if receber:
                log.info("Recebi mensagens")
                for dados in receber:
                    self.valores.append(dados.dados["name"])

            time.sleep(10)
            enviarmsg = ""
            for i in self.valores:
                enviarmsg += i
                enviarmsg += " "


            log.info("enviando email")
            global enviar
            yag.send(
                to=enviar,
                subject="Mensagem do core",
                contents=enviarmsg
            )



