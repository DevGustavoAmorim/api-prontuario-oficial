from datetime import datetime
from typing import Any, Dict, Optional

from db.session import SessionLocal

from app.models.pdf_model import PDFFile
from app.repository.pdf_repository import PDFRepository


def _parse_iso_date(
    value: Optional[str]
) -> Optional[datetime]:

    if not value:
        return None

    try:
        return datetime.fromisoformat(value)

    except ValueError:
        return None


def _normalize_payload(
    data: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Dict[str, Any]:

    payload = dict(data or {})
    payload.update(kwargs)

    # Compatibilidade com integrações antigas

    if "cd_paciente" not in payload and "paciente_id" in payload:
        payload["cd_paciente"] = payload["paciente_id"]

    if "cd_atendimento" not in payload and "atendimento_id" in payload:
        payload["cd_atendimento"] = payload["atendimento_id"]

    if "nm_documento" not in payload and "filename" in payload:
        payload["nm_documento"] = payload["filename"]

    if "cd_tipo_documento" not in payload and "tipo" in payload:
        payload["cd_tipo_documento"] = payload["tipo"]

    payload["dh_documento_fechado"] = _parse_iso_date(
        payload.get("dh_fechamento")
    )

    payload["dh_documento_importado"] = _parse_iso_date(
        payload.get("dh_impresso")
    )

    return payload


def upload_pdf(
    documento_id: int,
    content: bytes,
    data: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Dict[str, Any]:

    if len(content) > 5 * 1024 * 1024:
        raise ValueError(
            "PDF excede o tamanho máximo permitido"
        )

    payload = _normalize_payload(
        data,
        **kwargs
    )

    try:
        payload["cd_paciente"] = int(
            payload.get("cd_paciente")
        )

    except (TypeError, ValueError) as exc:

        raise ValueError(
            "Campo 'cd_paciente' inválido"
        ) from exc

    return save_pdf(
        documento_id=documento_id,
        content=content,
        data=payload
    )


def save_pdf(
    documento_id: int,
    content: bytes,
    data: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Dict[str, Any]:

    payload = _normalize_payload(
        data,
        **kwargs
    )

    db = SessionLocal()

    try:

        repository = PDFRepository(db)

        pdf_existente = repository.get_by_id(
            documento_id
        )

        # UPDATE

        if pdf_existente:

            pdf_existente.cd_paciente = str(
                payload.get("cd_paciente")
            )

            pdf_existente.cd_atendimento = payload.get(
                "cd_atendimento"
            )

            pdf_existente.nm_paciente = (
                payload.get("nm_paciente")
                or ""
            )

            pdf_existente.cd_objeto = payload.get(
                "cd_objeto"
            )

            pdf_existente.cd_setor = payload.get(
                "cd_setor"
            )

            pdf_existente.nm_setor = payload.get(
                "nm_setor"
            )

            pdf_existente.cd_leito = payload.get(
                "cd_leito"
            )

            pdf_existente.ds_leito = payload.get(
                "ds_leito"
            )

            pdf_existente.cd_tipo_documento = payload.get(
                "cd_tipo_documento"
            )

            pdf_existente.ds_tipo_documento = (
                payload.get("ds_tipo_documento")
                or ""
            )

            pdf_existente.nm_documento = (
                payload.get("nm_documento")
                or ""
            )

            pdf_existente.tp_status = payload.get(
                "tp_status"
            )

            pdf_existente.dh_documento_fechado = payload.get(
                "dh_documento_fechado"
            )

            pdf_existente.dh_documento_importado = payload.get(
                "dh_documento_importado"
            )

            pdf_existente.pdf_blob = content

            repository.update(
                pdf_existente
            )

            db.commit()

            db.refresh(
                pdf_existente
            )

            return {
                "id": pdf_existente.id,
                "updated": True,
                "size": len(content),
                "message": "PDF atualizado com sucesso"
            }

        # INSERT

        novo_pdf = PDFFile(

            id=documento_id,

            cd_paciente=str(
                payload.get("cd_paciente")
            ),

            cd_atendimento=payload.get(
                "cd_atendimento"
            ),

            nm_paciente=(
                payload.get("nm_paciente")
                or ""
            ),

            cd_objeto=payload.get(
                "cd_objeto"
            ),

            cd_setor=payload.get(
                "cd_setor"
            ),

            nm_setor=payload.get(
                "nm_setor"
            ),

            cd_leito=payload.get(
                "cd_leito"
            ),

            ds_leito=payload.get(
                "ds_leito"
            ),

            cd_tipo_documento=payload.get(
                "cd_tipo_documento"
            ),

            ds_tipo_documento=(
                payload.get("ds_tipo_documento")
                or ""
            ),

            nm_documento=(
                payload.get("nm_documento")
                or ""
            ),

            tp_status=payload.get(
                "tp_status"
            ),

            dh_documento_fechado=payload.get(
                "dh_documento_fechado"
            ),

            dh_documento_importado=payload.get(
                "dh_documento_importado"
            ),

            pdf_blob=content
        )

        repository.save(
            novo_pdf
        )

        db.commit()

        db.refresh(
            novo_pdf
        )

        return {
            "id": novo_pdf.id,
            "updated": False,
            "size": len(content),
            "message": "PDF salvo com sucesso"
        }

    except Exception as exc:

        db.rollback()

        raise RuntimeError(
            f"Falha ao salvar PDF: {exc}"
        ) from exc

    finally:

        db.close()


def get_pdf(
    documento_id: int
):

    db = SessionLocal()

    try:

        repository = PDFRepository(db)

        return repository.get_pdf_file(
            documento_id
        )

    finally:

        db.close()