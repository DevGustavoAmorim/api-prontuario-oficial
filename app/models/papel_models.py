from sqlalchemy import Column, Integer, String
from db.base import Base
from sqlalchemy.orm import relationship


class Papel(Base):
    """
    Modelo de dados para a tabela 'papeis' no banco de dados.
    Define os níveis de acesso (SYS, MASTER, SUPERVISOR, USUARIO_UNIDADE).
    """
    __tablename__ = "papeis"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)

    # Relacionamento reverso para rastrear os vínculos associados a este papel
    vinculos = relationship("VinculoUsuarioEmpresa", back_populates="papel")
