import logging
import threading
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("mensagens")

_PARAR = object()  # sinal interno para encerrar a thread


@dataclass
class Mensagem:
    de : str
    para : str
    tipo: str
    dados: dict[str, Any] = field(default_factory=dict)


class CaixaDeMensagens:

    def __init__(self):
        self._mensagens: list[Mensagem] = []
        self._lock = threading.Lock()

    def enviar(self, mensagem: Mensagem):
        with self._lock:
            self._mensagens.append(mensagem)

    def receber(self, nome: str) -> Optional[list[Mensagem]]:

        with self._lock:
            minhas = [m for m in self._mensagens if m.para == nome]
            print(minhas)
            self._mensagens = [m for m in self._mensagens if m.para != nome]
            print(self._mensagens)
        return minhas or None