from pydantic import BaseModel
from typing import List, Optional

from app.schemas.documento_schema import DocumentoResponse


class AtendimentoResponse(BaseModel):
    atendimento: str
    paciente: str
    nome: Optional[str]
    idade: Optional[int]

    dataAtendimento: Optional[str]

    setor: Optional[str]
    leito: Optional[str]

    status: Optional[str]

    ultimoDocumento: Optional[str]

    documentos: List[DocumentoResponse]