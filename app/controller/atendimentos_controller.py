from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import SessionLocal
from app.models.pdf_model import PDFFile

router = APIRouter(
    prefix="/atendimentos",
    tags=["Atendimentos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================================================
# LISTAR TODOS OS ATENDIMENTOS
# ==================================================
@router.get("/")
def listar_atendimentos(db: Session = Depends(get_db)):

    registros = (
        db.query(PDFFile)
        .order_by(PDFFile.dh_documento_fechado.desc())
        .all()
    )

    if not registros:
        return []

    atendimentos = {}

    for item in registros:

        atendimento_id = str(item.cd_atendimento)

        if atendimento_id not in atendimentos:

            atendimentos[atendimento_id] = {
                "atendimento": atendimento_id,
                "paciente": item.cd_paciente,
                "nome": item.nm_paciente,
                "idade": None,
                "dataAtendimento": (
                    item.dh_documento_fechado.strftime("%d/%m/%Y")
                    if item.dh_documento_fechado
                    else None
                ),
                "setor": item.nm_setor,
                "leito": item.ds_leito or item.cd_leito,
                "status": item.tp_status or "ATIVO",
                "ultimoDocumento": (
                    item.dh_documento_fechado.strftime("%H:%M")
                    if item.dh_documento_fechado
                    else None
                ),
                "documentos": []
            }

        atendimentos[atendimento_id]["documentos"].append({
            "id": item.id,
            "nome": item.nm_documento,
            "data": (
                item.dh_documento_fechado.strftime("%d/%m/%Y")
                if item.dh_documento_fechado
                else None
            ),
            "arquivo": f"/pdf/{item.id}"
        })

    return list(atendimentos.values())


# ==================================================
# BUSCAR UM ATENDIMENTO ESPECÍFICO
# ==================================================
@router.get("/{cd_atendimento}")
def obter_atendimento(
    cd_atendimento: str,
    db: Session = Depends(get_db)
):

    documentos = (
        db.query(PDFFile)
        .filter(PDFFile.cd_atendimento == cd_atendimento)
        .order_by(PDFFile.dh_documento_fechado.desc())
        .all()
    )

    if not documentos:
        raise HTTPException(
            status_code=404,
            detail="Atendimento não encontrado"
        )

    ultimo = documentos[0]

    return {
        "atendimento": cd_atendimento,
        "paciente": ultimo.cd_paciente,
        "nome": ultimo.nm_paciente,
        "idade": None,
        "dataAtendimento": (
            ultimo.dh_documento_fechado.strftime("%d/%m/%Y")
            if ultimo.dh_documento_fechado
            else None
        ),
        "setor": ultimo.nm_setor,
        "leito": ultimo.ds_leito or ultimo.cd_leito,
        "status": ultimo.tp_status or "ATIVO",
        "ultimoDocumento": (
            ultimo.dh_documento_fechado.strftime("%H:%M")
            if ultimo.dh_documento_fechado
            else None
        ),
        "documentos": [
            {
                "id": doc.id,
                "nome": doc.nm_documento,
                "data": (
                    doc.dh_documento_fechado.strftime("%d/%m/%Y")
                    if doc.dh_documento_fechado
                    else None
                ),
                "arquivo": f"/pdf/{doc.id}"
            }
            for doc in documentos
        ]
    }