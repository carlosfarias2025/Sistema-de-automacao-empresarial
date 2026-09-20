from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from tablesSQL import User,Automation

import logging

from Database.connection import database

from msg_core import Mensagem, CaixaDeMensagens

logger = logging.getLogger(__name__)

class ServicoUsuario:
    """Centraliza operações de usuário, senha e tokens de acesso."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        msg: CaixaDeMensagens = None,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.msg = msg
    @staticmethod
    def gerar_hash_senha(senha_plana: str) -> str:
        hash_bytes = bcrypt.hashpw(senha_plana.encode("utf-8"), bcrypt.gensalt())
        return hash_bytes.decode("utf-8")

    @staticmethod
    def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
        return bcrypt.checkpw(
            senha_plana.encode("utf-8"), senha_hash.encode("utf-8")
        )

    @staticmethod
    def buscar_usuario_por_username(username: str):
        try:
            return database.buscar_str("users","name",username)
        except ValueError as v:
            logger.exception(v)

    def criar_usuario(
        self, username: str, fullname: str, email: str, senha_plana: str
    ) -> bool:
            usuario_existente = database.buscar_str("users","name",username)
            email_existente = database.buscar_str("users","email",email)

            if usuario_existente is not None:
                return False

            if email_existente is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="email já existe"
                )

            database.commit(
                User(
                    name=username,
                    full_name=fullname,
                    email=email,
                    password=self.gerar_hash_senha(senha_plana),
                )
            )
            return True

    def autenticar_usuario(self, name: str, senha: str):
        usuario = self.buscar_usuario_por_username(name)
        if usuario is None or not self.verificar_senha(senha, usuario.password):
            return None
        return usuario

    def criar_access_token(self, dados: dict) -> str:
        to_encode = dados.copy()
        expira_em = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )
        to_encode.update({"exp": expira_em})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def obter_usuario_atual(self, token: str):
        credenciais_invalidas = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credenciais_invalidas
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado")
        except jwt.InvalidTokenError:
            raise credenciais_invalidas

        usuario = self.buscar_usuario_por_username(username)
        if usuario is None:
            raise credenciais_invalidas
        return usuario

    def usuario_atual_dependencia(
        self, token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))
    ):
        return self.obter_usuario_atual(token)

    @staticmethod
    def adicionar_automacao(automacao:Automation):
        database.commit(automacao)

    @staticmethod
    def verificar_email(email: str):
        email = database.buscar_str("users","email",email)
        if email is not None:
            return True

        return False

    @staticmethod
    def retornar_automacoes(user:User):
        return database.buscar_str("automations","user_id",user.id,all=True)