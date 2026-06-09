from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.pacientes_model import Paciente
from db.session import SessionLocal

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def listar_pacientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return (
        db.query(Paciente)
        .order_by(Paciente.nm_paciente)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{cd_paciente}")
def obter_paciente(
    cd_paciente: int,
    db: Session = Depends(get_db)
):
    paciente = (
        db.query(Paciente)
        .filter(Paciente.cd_paciente == cd_paciente)
        .first()
    )

    if not paciente:
        raise HTTPException(
            status_code=404,
            detail="Paciente não encontrado"
        )

    return paciente