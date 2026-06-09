from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import SessionLocal
from app.models.leitos_model import Leito

router = APIRouter(
    prefix="/leitos",
    tags=["Leitos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def listar_leitos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return (
        db.query(Leito)
        .order_by(Leito.nm_leito)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{cd_leito}")
def obter_leito(
    cd_leito: int,
    db: Session = Depends(get_db)
):
    leito = (
        db.query(Leito)
        .filter(Leito.cd_leito == cd_leito)
        .first()
    )

    if not leito:
        raise HTTPException(
            status_code=404,
            detail="Leito não encontrado"
        )

    return leito