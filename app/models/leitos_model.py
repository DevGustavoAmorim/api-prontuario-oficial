from sqlalchemy import Column, Integer, String
from db.base import Base

class Leito(Base):
    __tablename__ = "leitos"

    cd_leito = Column(Integer, primary_key=True, index=True)
    ds_leito = Column(String, nullable=False)

