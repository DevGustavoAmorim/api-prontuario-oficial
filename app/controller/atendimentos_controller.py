from fastapi import APIRouter, HTTPException

from app.schemas.atendimentos_schema import (
    AtendimentoResponse
)

from app.services.atendimentos_service import (
    listar_atendimentos,
    obter_atendimento
)

router = APIRouter(
    prefix="/atendimentos",
    tags=["Atendimentos"]
)


@router.get(
    "/",
    response_model=list[AtendimentoResponse]
)
def listar():

    return listar_atendimentos()


@router.get(
    "/{cd_atendimento}",
    response_model=AtendimentoResponse
)
def buscar(cd_atendimento: str):

    atendimento = obter_atendimento(
        cd_atendimento
    )

    if not atendimento:
        raise HTTPException(
            status_code=404,
            detail="Atendimento não encontrado"
        )

    return atendimento