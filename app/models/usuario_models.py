from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class Usuario(Base):
    """
    Modelo de dados para a tabela 'usuarios' no banco de dados.
    """
    __tablename__ = "usuarios"

    cd_usuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)

    # Relacionamento Multiempresa já existente
    vinculos = relationship("VinculoUsuarioEmpresa", back_populates="usuario")

    # NOVO RELACIONAMENTO: Acesso direto às unidades de internação permitidas
    # Obs: Altere "UnidadeInternacao" para o nome exato da sua classe de unidades
    unidades = relationship(
        "Unid_Int", 
        secondary="Usuario_Unid_Int", 
        back_populates="usuarios"
    )



class VinculoUsuarioEmpresa(Base):
    """
    Tabela intermediária (Muitos-para-Muitos) que gerencia o ecossistema Multiempresa.
    Vincula um Usuário a uma Empresa específica com um Papel (Role) determinado.
    """
    __tablename__ = "vinculos_usuario_empresa"

    id = Column(Integer, primary_key=True, index=True)
    
    # Chaves Estrangeiras conectando as 3 pontas do sistema
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    # Mantive 'empresas.cd_empresa' com base no seu relacionamento anterior
    empresa_id = Column(Integer, ForeignKey("empresas.cd_empresa"), nullable=True) # Nullable=True permite o vínculo do SYS (Sem Empresa)
    papel_id = Column(Integer, ForeignKey("papeis.id"), nullable=True)

    # Relacionamentos para carregar os objetos do banco dinamicamente no Python
    usuario = relationship("Usuario", back_populates="vinculos")
    papel = relationship("Papel", back_populates="vinculos")  # Adicionado back_populates
    empresa = relationship("Empresa", back_populates="vinculos")  # Adicionado back_populates

