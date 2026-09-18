from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

import os
from dotenv import load_dotenv

from tablesSQL import Base, User
from sqlalchemy import create_engine

from servico_usuario import ServicoUsuario

load_dotenv()
password = os.getenv("POSTGRES_PASSWORD")
DATABASE_URL = f"postgresql+psycopg://postgres:&{password}@localhost:5432/datasystem"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI(title="Sistema de automação empresarial")
servico_usuario = ServicoUsuario(engine=engine, secret_key=SECRET_KEY)


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

class CadastroUsuario(BaseModel):
    full_name:str
    name: str
    password: str
    email:str

@app.get("/")
def seila():
    return {"status": "ok"}

@app.post("/registrar")
def registrar(newuser:CadastroUsuario):
    try:
        usuario_criado = servico_usuario.criar_usuario(
            username=newuser.name,
            fullname=newuser.full_name,
            email=newuser.email,
            senha_plana=servico_usuario.gerar_hash_senha(newuser.password),
        )
    except:
         raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR_CONFLICT,
             detail="Falha na criação de usuario"
         )
    if not usuario_criado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="usuário já existe"
        )
    token = servico_usuario.criar_access_token(
        dados={"sub":newuser.name,"role":"user"}
    )
    return{"access_token":token}


@app.get("/users/{user_id}")
def retornarusers(user_id: int):
    user = servico_usuario.buscar_usuario_por_id(user_id)
    if user is None:
        return {"error":"Usuario não existe"}
    return {"username":user.username,"fullname":user.fullname,"email":user.email}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = servico_usuario.autenticar_usuario(form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )

    # O payload carrega o que os outros serviços/rotas precisam saber
    # sobre esse usuário, sem precisar consultar o banco de novo.
    access_token = servico_usuario.criar_access_token(
        dados={"sub": usuario.username, "role": "user"}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/perfil")
def ler_perfil(usuario_atual: User = Depends(servico_usuario.usuario_atual_dependencia)):
    return {
        "username": usuario_atual.name,
        "full_name": usuario_atual.full_name,
        "role": "user",
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("API_REST_HOST_ORIGIN_LOCALHOST"),
                             os.getenv("API_REST_HOST_ORIGIN")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
