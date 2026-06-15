from sqlalchemy import Column, String, Boolean
from db.base import Base
from sqlalchemy.orm import relationship


class Empresa(Base):
    """
    Modelo de dados para a tabela 'empresas' no banco de dados.
    Retorna os atributos de uma empresa, incluindo código, nome, CNPJ e status ativo.
    """

    # Nome da tabela no banco de dados
    __tablename__ = "empresas"

    # Mantido como String(20) conforme sua definição original.
    # Lembre-se: No seu script de sementes (seed), o valor deve ser enviado como texto (ex: "1").
    cd_empresa = Column(String(20), primary_key=True) 

    nome = Column(String(150), nullable=False)

    cnpj = Column(String(20), unique=True)

    ativo = Column(Boolean, default=True)

    # Relacionamento que permite listar todos os vínculos/funcionários desta empresa
    vinculos = relationship("VinculoUsuarioEmpresa", back_populates="empresa")
