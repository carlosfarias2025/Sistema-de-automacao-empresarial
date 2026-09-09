from sqlalchemy import create_engine, text
from backend.tablesSQL import Base

DATABASE_URL = "postgresql+psycopg://postgres:carlos123@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

with engine.connect() as connection:
    result = connection.execute(text("SELECT version()"))
    print(result.fetchone())