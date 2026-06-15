from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.empresa_models import Empresa
from app.schemas.empresa_schema import EmpresaCreate
from app.utils.cnpj_utils import limpar_cnpj, formatar_cnpj

def criar_empresa_service(empresa: EmpresaCreate, db: Session):
    
    # Validador de Empresa_Service -> Limpa cnpj para comparação no banco
    cnpj_limpo = limpar_cnpj(empresa.cnpj)

    existe = db.query(Empresa).filter(Empresa.cnpj == cnpj_limpo).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="CNPJ já cadastrado"
        )
    
    nova = Empresa(
        nome=empresa.nome,
        cnpj=cnpj_limpo,
        cd_empresa=empresa.cd_empresa
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)

    return nova