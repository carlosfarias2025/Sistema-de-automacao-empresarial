import threading
from main import run
from core import Core
from msg_core import CaixaDeMensagens

msg = CaixaDeMensagens()

core = Core(msg)
core.start()

api = threading.Thread(target=run,args=([msg]), daemon=True)
api.start()


api.join()
