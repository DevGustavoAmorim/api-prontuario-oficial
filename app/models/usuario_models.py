from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship


class Usuario(Base):
    """
    Modelo de dados para a tabela 'usuarios' no banco de dados.
    Guarda apenas os dados cadastrais e de autenticação do usuário.
    Os papéis e empresas agora são gerenciados pela tabela de vínculos.
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)

    # Relacionamento para conseguir acessar todos os vínculos do usuário a partir dele
    vinculos = relationship("VinculoUsuarioEmpresa", back_populates="usuario")


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

