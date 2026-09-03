"""
Exemplo de autenticação JWT (HS256) com FastAPI.

Fluxo:
1. POST /login          -> valida usuário/senha e devolve um access token JWT
2. GET  /perfil          -> rota protegida, exige "Authorization: Bearer <token>"

Para rodar:
    pip install fastapi pyjwt bcrypt python-multipart uvicorn
    uvicorn auth_jwt_exemplo:app --reload

Depois abra http://127.0.0.1:8000/docs para testar pelo Swagger.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# ---------------------------------------------------------------------------
# Configuração da chave JWT
# ---------------------------------------------------------------------------
# Em produção, essa chave NUNCA fica hardcoded no código: vem de variável de
# ambiente / secret manager. É uma única chave do servidor de autenticação,
# não uma chave por usuário (ver explicação no chat).
SECRET_KEY = "troque-isso-por-uma-chave-forte-e-aleatoria"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

app = FastAPI(title="Exemplo JWT - HS256")

# ---------------------------------------------------------------------------
# Hash de senha usando bcrypt diretamente (sem passlib)
# ---------------------------------------------------------------------------
def gerar_hash_senha(senha_plana: str) -> str:
    hash_bytes = bcrypt.hashpw(senha_plana.encode("utf-8"), bcrypt.gensalt())
    return hash_bytes.decode("utf-8")


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha_plana.encode("utf-8"), senha_hash.encode("utf-8"))


# ---------------------------------------------------------------------------
# "Banco de dados" fake, só para o exemplo
# ---------------------------------------------------------------------------
fake_users_db = {
    "joao": {
        "username": "joao",
        "full_name": "João Silva",
        # senha real: "senha123" (hash gerado com bcrypt)
        "hashed_password": gerar_hash_senha("senha123"),
        "role": "admin",
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def autenticar_usuario(username: str, senha: str):
    usuario = fake_users_db.get(username)
    if not usuario:
        return None
    if not verificar_senha(senha, usuario["hashed_password"]):
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
    """
    Roda em toda rota protegida. Decodifica e valida o token:
    - assinatura correta? (ninguém alterou o payload)
    - não expirou?
    Se tudo ok, devolve os dados do usuário extraídos do próprio token
    -- sem precisar consultar banco nenhum para isso.
    """
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

    usuario = fake_users_db.get(username)
    if usuario is None:
        raise credenciais_invalidas
    return usuario


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.get("/")
def seila():
    return {"status": "ok"}
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
        dados={"sub": usuario["username"], "role": usuario["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/perfil")
def ler_perfil(usuario_atual: dict = Depends(obter_usuario_atual)):
    return {
        "username": usuario_atual["username"],
        "full_name": usuario_atual["full_name"],
        "role": usuario_atual["role"],
    }