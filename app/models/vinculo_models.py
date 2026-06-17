# app/models/vinculo_models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from db.base import Base
from sqlalchemy.orm import relationship

class VinculoUsuarioEmpresa(Base):
    """
    Tabela intermediária (Muitos-para-Muitos) que gerencia o ecossistema Multiempresa.
    Vincula um Usuário a uma Empresa específica com um Papel (Role) determinado.
    """
    __tablename__ = "vinculos_usuario_empresa"

    id = Column(Integer, primary_key=True, index=True)
    
    # Chaves Estrangeiras conectando as 3 pontas do sistema
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # IMPORTANTE: Como 'cd_empresa' no seu Empresa model é String(20), 
    # a chave estrangeira aqui também precisa ser String(20) para o banco aceitar a união.
    empresa_id = Column(String(20), ForeignKey("empresas.cd_empresa"), nullable=True) # Nullable=True para o SYS
    
    papel_id = Column(Integer, ForeignKey("papeis.id"), nullable=False)

    # Relacionamentos para carregar os objetos do banco dinamicamente no Python
    usuario = relationship("Usuario", back_populates="vinculos")
    papel = relationship("Papel", back_populates="vinculos")
    empresa = relationship("Empresa", back_populates="vinculos")
