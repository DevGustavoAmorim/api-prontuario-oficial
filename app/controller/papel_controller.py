from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from app.models.papel_models import Papel

router = APIRouter(prefix="/papel", tags=["Papel"])


@router.post("/")
def criar_role(nome: str, db: Session = Depends(get_db)):

    role = Papel(nome=nome)

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


@router.get("/")
def listar_roles(db: Session = Depends(get_db)):

    return db.query(Papel).all()