from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.papel_models import Papel


def criar_papel_service(nome_papel: str, db: Session):

    # valida duplicidade
    existe = db.query(Papel).filter(Papel.nome == nome_papel).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Papel já existe"
        )

    novo_papel = Papel(nome=nome_papel)

    db.add(novo_papel)
    db.commit()
    db.refresh(novo_papel)

    return novo_papel