from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base

class Unid_Int(Base):
    __tablename__ = "Unid_Int"

    cd_unid_int = Column(Integer, primary_key=True, index=True)
    ds_unid_int = Column(String(150), nullable=False)

    # CORREÇÃO: Aponta para a classe 'Leito' (singular) e faz o back_populates com 'unidade'
    leitos = relationship("Leito", back_populates="unidade")
