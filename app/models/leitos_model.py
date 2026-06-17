from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base

class Leito(Base):
    __tablename__ = "leitos"

    cd_leito = Column(Integer, primary_key=True, index=True)
    ds_leito = Column(String, nullable=False)
    
    # 1. CORREÇÃO: Tipo alterado para Integer e adicionado ForeignKey
    cd_unid_int = Column(Integer, ForeignKey("Usuario_Unid_Int.cd_unid_int"), nullable=False)

    # Variavel é uma chave para colocar na tabela relacionada
    unidade = relationship("Usuario_Unid_Int", back_populates="leitos")
