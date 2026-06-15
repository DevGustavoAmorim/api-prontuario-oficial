from pydantic import BaseModel

class VinculoCreate(BaseModel):
    usuario_id: int
    empresa_id: str  # String para casar com cd_empresa
    papel_id: int    # Ex: 2 para MASTER, 3 para SUPERVISOR
