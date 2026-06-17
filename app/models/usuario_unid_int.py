from sqlalchemy import Column, Integer, ForeignKey
from db.base import Base

class UsuarioUnidInt(Base):
    """
    Tabela Associativa: Vincula Usuários às Unidades de Internação
    """
    __tablename__ = "Usuario_Unid_Int"

    # Chave primária composta para garantir registros únicos de vínculo
    cd_usuario = Column(Integer, primary_key=True)
    cd_unid_int = Column(Integer, ForeignKey("unidades_internacao.cd_unid_int"), primary_key=True)
