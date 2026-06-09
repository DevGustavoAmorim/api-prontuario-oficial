from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON
from db.base import Base


class Configuracoes(Base):
    __tablename__ = 'configuracoes'

    id = Column(Integer, primary_key=True, index=True)
    tempo_prontuarios = Column(Integer, nullable=False, default=30)
    documentos_por_setor = Column(JSON, nullable=False, default=dict)
    outras_configuracoes = Column(JSON, nullable=False, default=dict)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'tempo_prontuarios': self.tempo_prontuarios,
            'documentos_por_setor': self.documentos_por_setor,
            'outras_configuracoes': self.outras_configuracoes,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
        }

    def __repr__(self) -> str:
        return f"<Configuracoes id={self.id} ativo={self.ativo} tempo_prontuarios={self.tempo_prontuarios}>"
