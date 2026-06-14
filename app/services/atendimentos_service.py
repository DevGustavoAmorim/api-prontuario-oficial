from typing import Optional

from db.session import SessionLocal

from app.repository.atendimentos_repository import (
    AtendimentoRepository
)


def _formatar_documento(doc) -> dict:
    """
    Converte um documento do banco
    para o formato de resposta da API.
    """

    return {
        "id": doc.id,
        "nome": doc.nm_documento,
        "data": (
            doc.dh_documento_fechado.strftime("%d/%m/%Y")
            if doc.dh_documento_fechado
            else None
        ),
        "arquivo": f"/pdf/{doc.id}"
    }


def _formatar_atendimento(item) -> dict:
    """
    Converte um registro PDF
    para o formato de atendimento.
    """

    return {
        "atendimento": str(item.cd_atendimento),
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


def listar_atendimentos() -> list[dict]:
    """
    Lista todos os atendimentos agrupando
    os documentos por atendimento.
    """

    db = SessionLocal()

    try:

        repository = AtendimentoRepository(db)

        registros = repository.listar_atendimentos()

        if not registros:
            return []

        atendimentos = {}

        for item in registros:

            atendimento_id = str(
                item.cd_atendimento
            )

            if atendimento_id not in atendimentos:

                atendimentos[
                    atendimento_id
                ] = _formatar_atendimento(item)

            atendimentos[
                atendimento_id
            ]["documentos"].append(
                _formatar_documento(item)
            )

        return list(
            atendimentos.values()
        )

    finally:
        db.close()


def obter_atendimento(
    cd_atendimento: str
) -> Optional[dict]:
    """
    Busca um atendimento específico.
    """

    db = SessionLocal()

    try:

        repository = AtendimentoRepository(db)

        documentos = (
            repository.buscar_por_atendimento(
                cd_atendimento
            )
        )

        if not documentos:
            return None

        ultimo = documentos[0]

        atendimento = _formatar_atendimento(
            ultimo
        )

        atendimento["documentos"] = [

            _formatar_documento(doc)

            for doc in documentos
        ]

        return atendimento

    finally:
        db.close()