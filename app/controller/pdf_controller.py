from typing import Optional
from datetime import datetime
from io import BytesIO

from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    UploadFile,
    File,
    Form
)

from fastapi.responses import StreamingResponse

from db.session import SessionLocal

from app.models.pdf_model import PDFFile
from app.models.pacientes_model import Paciente
from app.models.setores_model import Setor
from app.models.leitos_model import Leito

router = APIRouter(
    prefix="/pdf",
    tags=["PDF"]
)


def parse_iso_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@router.post("/upload_blob")
async def upload_pdf_blob(
    request: Request,
    file: UploadFile = File(...),
    cd_paciente: str = Form(...),
    cd_atendimento: str = Form(...),
    nm_paciente: str = Form(...),
    cd_objeto: Optional[str] = Form(None),
    cd_setor: Optional[str] = Form(None),
    nm_setor: Optional[str] = Form(None),
    cd_leito: Optional[str] = Form(None),
    ds_leito: Optional[str] = Form(None),
    cd_tipo_documento: Optional[str] = Form(None),
    ds_tipo_documento: Optional[str] = Form(None),
    nm_documento: Optional[str] = Form(None),
    dh_fechamento: Optional[str] = Form(None),
    dh_impresso: Optional[str] = Form(None),
    tp_status: Optional[str] = Form(None)
):
    db = SessionLocal()

    try:

        id_param = request.query_params.get("id")

        if not id_param:
            raise HTTPException(
                status_code=400,
                detail="Parâmetro 'id' obrigatório"
            )

        try:
            documento_id = int(id_param)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Parâmetro 'id' inválido"
            )

        content = await file.read()

        tamanho = len(content)

        MAX_SIZE = 5 * 1024 * 1024

        if tamanho > MAX_SIZE:
            raise HTTPException(
                status_code=413,
                detail="PDF excede o tamanho máximo permitido"
            )

        pdf_existente = (
            db.query(PDFFile)
            .filter(PDFFile.id == documento_id)
            .first()
        )

        is_update = pdf_existente is not None

        paciente = (
            db.query(Paciente)
            .filter(
                Paciente.cd_paciente == int(cd_paciente)
            )
            .first()
        )

        if not paciente:
            paciente = Paciente(
                cd_paciente=int(cd_paciente),
                nm_paciente=nm_paciente
            )
            db.add(paciente)
        else:
            paciente.nm_paciente = nm_paciente

        if cd_setor and nm_setor:

            setor = (
                db.query(Setor)
                .filter(Setor.cd_setor == cd_setor)
                .first()
            )

            if not setor:
                setor = Setor(
                    cd_setor=cd_setor,
                    nm_setor=nm_setor
                )
                db.add(setor)

        if cd_leito and ds_leito:

            leito = (
                db.query(Leito)
                .filter(Leito.cd_leito == cd_leito)
                .first()
            )

            if not leito:
                leito = Leito(
                    cd_leito=cd_leito,
                    ds_leito=ds_leito
                )
                db.add(leito)

        if is_update:

            pdf_existente.cd_paciente = cd_paciente
            pdf_existente.cd_atendimento = cd_atendimento
            pdf_existente.nm_paciente = nm_paciente
            pdf_existente.cd_objeto = cd_objeto
            pdf_existente.cd_setor = cd_setor
            pdf_existente.nm_setor = nm_setor
            pdf_existente.cd_leito = cd_leito
            pdf_existente.ds_leito = ds_leito
            pdf_existente.cd_tipo_documento = cd_tipo_documento
            pdf_existente.ds_tipo_documento = ds_tipo_documento or ""
            pdf_existente.nm_documento = nm_documento or ""
            pdf_existente.tp_status = tp_status
            pdf_existente.dh_documento_fechado = parse_iso_date(dh_fechamento)
            pdf_existente.dh_documento_importado = parse_iso_date(dh_impresso)
            pdf_existente.pdf_blob = content

            db.add(pdf_existente)

        else:

            novo_pdf = PDFFile(
                id=documento_id,
                cd_paciente=cd_paciente,
                cd_atendimento=cd_atendimento,
                nm_paciente=nm_paciente,
                cd_objeto=cd_objeto,
                cd_setor=cd_setor,
                nm_setor=nm_setor,
                cd_leito=cd_leito,
                ds_leito=ds_leito,
                cd_tipo_documento=cd_tipo_documento,
                ds_tipo_documento=ds_tipo_documento or "",
                nm_documento=nm_documento or "",
                tp_status=tp_status,
                dh_documento_fechado=parse_iso_date(dh_fechamento),
                dh_documento_importado=parse_iso_date(dh_impresso),
                pdf_blob=content
            )

            db.add(novo_pdf)

        db.commit()

        return {
            "message": "PDF salvo com sucesso" if not is_update else "PDF atualizado com sucesso",
            "id": documento_id,
            "size": tamanho,
            "updated": is_update
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

    finally:
        db.close()


@router.get("/{id}")
def obter_pdf(id: int):

    db = SessionLocal()

    try:

        pdf = (
            db.query(PDFFile)
            .filter(PDFFile.id == id)
            .first()
        )

        if not pdf:
            raise HTTPException(
                status_code=404,
                detail="PDF não encontrado"
            )

        return StreamingResponse(
            BytesIO(pdf.pdf_blob),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{pdf.nm_documento}"'
            }
        )

    finally:
        db.close()