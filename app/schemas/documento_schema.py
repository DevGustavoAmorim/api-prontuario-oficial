from pydantic import BaseModel
from typing import Optional


class DocumentoResponse(BaseModel):
    id: int
    nome: Optional[str]
    data: Optional[str]
    arquivo: str