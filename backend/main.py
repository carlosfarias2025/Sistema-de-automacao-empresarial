from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

import os
from dotenv import load_dotenv

from dataclasses import dataclass

from tablesSQL import Base,User
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session

load_dotenv()
password = os.getenv("POSTGRES_PASSWORD")
DATABASE_URL = f"postgresql+psycopg://postgres:&{password}@localhost:5432/datasystem"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

@dataclass
class UserData:
    username: str
    full_name: str
    hashed_password: str
    role: str



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

app = FastAPI(title="Sistema de automação empresarial")


def gerar_hash_senha(senha_plana: str) -> str:
    hash_bytes = bcrypt.hashpw(senha_plana.encode("utf-8"), bcrypt.gensalt())
    return hash_bytes.decode("utf-8")


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha_plana.encode("utf-8"), senha_hash.encode("utf-8"))


# ---------------------------------------------------------------------------
# "Banco de dados" fake, só para o exemplo
# ---------------------------------------------------------------------------


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def autenticar_usuario(username: str, senha: str):
    with Session(engine) as session:
        usuario = session.scalar(select(User).where(User.username == username))
        if usuario is None:
            return None
        if not verificar_senha(senha, usuario.password):
            return None

        return usuario


def criar_access_token(dados: dict) -> str:
    """
    Monta o payload (claims), define expiração e assina o token com a
    chave secreta usando HS256. O resultado é uma string "header.payload.signature".
    """
    to_encode = dados.copy()
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expira_em})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def obter_usuario_atual(token: str = Depends(oauth2_scheme)):
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credenciais_invalidas
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise credenciais_invalidas
    with Session(engine) as session:
        usuario = session.scalar(select(User).where(User.username == username))
        if usuario is None:
            raise credenciais_invalidas
        return usuario


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

class CadastroUsuario(BaseModel):
    fullname:str
    nameuser: str
    password: str
    email:str

@app.get("/")
def seila():
    return {"status": "ok"}

@app.post("/registrar")
def registrar(newuser:CadastroUsuario):

    usersql = User(
        username=newuser.nameuser,
        fullname=newuser.fullname,
        email=newuser.email,
        password=gerar_hash_senha(newuser.password),
    )

    try:
        with Session(engine) as session:
            seuserexit = session.scalar(select(User).where(User.username == newuser.nameuser))
            if seuserexit is None:
                session.add(usersql)
                session.commit()
    except:
         raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR_CONFLICT,
             detail="Falha na criação de usuario"
         )
    if seuserexit:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="usuário já existe"
        )
    token = criar_access_token(dados={"sub":newuser.nameuser,"role":"user"})
    return{"access_token":token}


@app.get("/users/{user_id}")
def retornarusers(user_id: int):
    with Session(engine) as session:
        user = session.scalar(select(User).where(User.id == user_id))
        if user is None:
            return {"error":"Usuario não existe"}
        else:
            return {"username":user.username,"fullname":user.fullname,"email":user.email}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = autenticar_usuario(form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )

    # O payload carrega o que os outros serviços/rotas precisam saber
    # sobre esse usuário, sem precisar consultar o banco de novo.
    access_token = criar_access_token(
        dados={"sub": usuario.username, "role": "user"}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/perfil")
def ler_perfil(usuario_atual: User = Depends(obter_usuario_atual)):
    return {
        "username": usuario_atual.username,
        "full_name": usuario_atual.fullname,
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