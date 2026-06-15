from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.schemas.empresa_schema import EmpresaResponse

# --- NOVO SCHEMA DE VÍNCULO ---
class VinculoResponse(BaseModel):
    """
    Schema que representa a resposta de um vínculo específico do usuário,
    detalhando o papel e a empresa associada.
    """
    id: int
    papel_id: int
    # Retorna os detalhes da empresa para este vínculo específico (pode ser None no caso do SYS)
    empresa: Optional[EmpresaResponse] = None

    class Config:
        from_attributes = True


# --- SCHEMA DE CRIAÇÃO ---
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr  # Força a validação de formato correto de e-mail
    senha: str
    papel_id: int
    # Como cd_empresa é String(20), recebemos como str. Opcional para o fluxo do MASTER herdar automaticamente
    empresa_id: Optional[str] = None


# --- SCHEMA DE RESPOSTA ---
class UsuarioResponse(BaseModel):
    """
    Params
     id: Identificador único do usuário.
     nome: Nome completo do usuário.
     email: Endereço de e-mail do usuário.
     ativo: Indica se o usuário está ativo.
     vinculos: Lista contendo todas as empresas e papéis atrelados a este usuário.
    """
    id: int
    nome: str
    email: str
    ativo: bool
    
    # MUDANÇA CRUCIAL: Em vez de campos engessados, retorna a lista de todos os vínculos multiempresa
    vinculos: List[VinculoResponse] = []

    class Config:
        from_attributes = True

# Adicione isso no final do seu arquivo app/schemas/usuario_schema.py

class EmpresasDoUsuarioResponse(BaseModel):
    id_vinculo: int
    papel_id: int
    papel_nome: str
    empresa: EmpresaResponse

    class Config:
        from_attributes = True
