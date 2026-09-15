from .Base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped,mapped_column

class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key=True)
    username:Mapped[str] = mapped_column(String)
    fullname:Mapped[str] = mapped_column(String)
    email:Mapped[str] = mapped_column(String)
    password:Mapped[str] = mapped_column(String)