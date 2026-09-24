from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

import os
from sqlalchemy.exc import IntegrityError
from sympy.codegen.ast import none

from msg_core import CaixaDeMensagens
from tablesSQL import User,Automation

from customer_service import ServicoUsuario

import logging
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("uvicorn")


SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI(title="Sistema de automação empresarial")

customerService: ServicoUsuario = ServicoUsuario(secret_key=SECRET_KEY)
# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

def run(msg : CaixaDeMensagens):
    global customerService
    customerService = ServicoUsuario(secret_key=SECRET_KEY,msg=msg)
    uvicorn.run(app, host="0.0.0.0", port=8000)

class CadastroUsuario(BaseModel):
    full_name:str
    name: str
    password: str
    email:str

class AutomacaoCreate(BaseModel):
    nome:str

@app.get("/")
def seila():
    return {"status": "ok"}

@app.post("/registrar")
def registrar(newuser:CadastroUsuario):

    try:
        usuario_criado = customerService.criar_usuario(
            username=newuser.name,
            fullname=newuser.full_name,
            email=newuser.email,
            senha_plana=newuser.password,
        )

    except IntegrityError:
         raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR_CONFLICT,
             detail="Falha na criação de usuario"
         )
    except HTTPException:
        raise
    if not usuario_criado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="usuário já existe"
        )
    token = customerService.criar_access_token(
        dados={"sub":newuser.name,"role":"user"}
    )
    return{"access_token":token}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = customerService.autenticar_usuario(form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )

    # O payload carrega o que os outros serviços/rotas precisam saber
    # sobre esse usuário, sem precisar consultar o banco de novo.
    access_token = customerService.criar_access_token(
        dados={"sub": usuario.name, "role": "user"}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/perfil")
def ler_perfil(usuario_atual: User = Depends(customerService.usuario_atual_dependencia)):
    return {
        "username": usuario_atual.name,
        "full_name": usuario_atual.full_name,
        "role": "user",
    }

@app.post("/automacao")
def criar_automacao(automacao: AutomacaoCreate,usuario_atual: User = Depends(customerService.usuario_atual_dependencia)):
    automation = Automation(
        user=usuario_atual,
        nome=automacao.nome,
    )
    customerService.adicionar_automacao(automation)
    return {
        "Automacao": automacao.nome
    }

@app.get("/my_automation")
def ler_automacao(usuario_atual: User = Depends(customerService.usuario_atual_dependencia)):
    automacoes = customerService.retornar_automacoes(usuario_atual)
    return_automacoes:dict[str,str] = {}

    for auto in automacoes:
        return_automacoes[auto.id] = auto.nome

    return return_automacoes


app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("API_REST_HOST_ORIGIN_LOCALHOST"),
                             os.getenv("API_REST_HOST_ORIGIN")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    run(CaixaDeMensagens())