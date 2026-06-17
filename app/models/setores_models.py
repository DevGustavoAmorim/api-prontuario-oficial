from sqlalchemy import Column, Integer, String
from db.base import Base

class Setor(Base):
    __tablename__ = "setores"

    cd_setor = Column(Integer, primary_key=True, index=True)
    nm_setor = Column(String, nullable=False)
