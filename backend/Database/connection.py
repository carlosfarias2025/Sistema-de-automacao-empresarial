# Database code

from sqlalchemy import select,create_engine
from sqlalchemy.orm import Session

import os
from dotenv import load_dotenv
import logging

from tablesSQL import User,Automation,Base

load_dotenv() #Loading .env
password = os.getenv("POSTGRES_PASSWORD")
DATABASE_URL = f"postgresql+psycopg://postgres:&{password}@localhost:5432/datasystem"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

logger = logging.getLogger(__name__)

class Database:
    @staticmethod
    def commit(obj) -> bool:
        try:
            with Session(engine) as session:
                session.add(obj)
                session.commit()
                session.refresh(obj)
            return True
        except Exception as e:
            logger.error(e)
            return False

    @staticmethod
    def buscar_id(nametable:str, num:int):
        name = Base.metadata.tables[nametable]
        stm = select(name).where(name.c.id == num)

        with Session(engine) as session:
            try:
                result = session.execute(stm)
                return result
            except Exception as e:
                logger.error(e)
                return None
    @staticmethod
    def buscar_str(nametable:str,columnname:str, string,*,all:bool=False) -> User |list |None  :
        class_retorn = None
        for mapper in Base.registry.mappers:
            if mapper.local_table.name == nametable:
                class_retorn = mapper.class_
                break

        if not class_retorn:
            raise ValueError(
                f"Tabela {nametable} não foi encontrada"
            )

        try:
            column_obj = getattr(class_retorn,columnname)
        except AttributeError:
            raise ValueError(
                f"A coluna {columnname} não foi encontrado"
            )

        stm = select(class_retorn).where(column_obj == string)

        with Session(engine) as session:
            try:
                if not all:
                    return session.execute(stm).scalar_one_or_none()
                else:
                    return list(session.execute(stm).scalars().all())
            except Exception as e:
                logger.error(e)
                return None

    @staticmethod
    def all(nametable: str, columnname: str, *, all: bool = False) -> User | list | None:
        class_retorn = None
        for mapper in Base.registry.mappers:
            if mapper.local_table.name == nametable:
                class_retorn = mapper.class_
                break

        if not class_retorn:
            raise ValueError(
                f"Tabela {nametable} não foi encontrada"
            )

        try:
            column_obj = getattr(class_retorn, columnname)
        except AttributeError:
            raise ValueError(
                f"A coluna {columnname} não foi encontrado"
            )

        stm = select(class_retorn)

        with Session(engine) as session:
            try:
                if not all:
                    return session.execute(stm).scalar_one_or_none()
                else:
                    return list(session.execute(stm).scalars().all())
            except Exception as e:
                logger.error(e)
                return None



database = Database()
