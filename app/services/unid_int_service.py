from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.unid_int_models import Unid_Int


def criar_unid_int_service(desc_Unid_Int: str, db: Session):

    # valida duplicidade
                    # Classe       Classe.Coluna
    existe = db.query(Unid_Int).filter(Unid_Int.nome == desc_Unid_Int).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Unidade de Internação já existe"
        )

    novo_ds_Unid_Int = Unid_Int(nome=desc_Unid_Int)

    db.add(novo_ds_Unid_Int)
    db.commit()
    db.refresh(novo_ds_Unid_Int)

    return novo_ds_Unid_Int