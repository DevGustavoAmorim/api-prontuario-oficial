# Importa o tipo Optional do módulo typing.
# Optional[str] significa que uma variável pode ser uma string OU None.
from typing import Optional

# Importa BytesIO.
# Permite transformar um array de bytes (blob do banco)
# em um arquivo que pode ser enviado ao navegador.
from io import BytesIO


# Importa os componentes principais do FastAPI.

# APIRouter:
# Permite organizar endpoints em módulos separados.
#
# Request:
# Representa a requisição HTTP recebida.
# Permite acessar headers, query params, cookies, etc.
#
# HTTPException:
# Utilizada para retornar erros HTTP padronizados.
#
# UploadFile:
# Representa um arquivo enviado pelo cliente.
#
# File:
# Informa ao FastAPI que o parâmetro é um arquivo.
#
# Form:
# Informa ao FastAPI que o parâmetro vem de multipart/form-data.
from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form


# StreamingResponse permite devolver arquivos para o cliente.
# Ideal para PDFs, imagens, vídeos e arquivos grandes.
from fastapi.responses import StreamingResponse


# Importa funções da camada Service.
#
# upload_pdf:
# Responsável pela regra de negócio do upload.
#
# get_pdf_service:
# Responsável pela busca do PDF.
#
# O controller não acessa banco diretamente.
# Ele delega a responsabilidade para a camada Service.
from app.services.pdf_service import get_pdf as get_pdf_service, upload_pdf


# Cria um agrupamento de rotas.
#
# Todas as rotas deste arquivo terão o prefixo /pdf.
#
# Exemplo:
# @router.post("/upload_blob")
# vira:
# POST /pdf/upload_blob
router = APIRouter(

    # Prefixo comum das rotas
    prefix="/pdf",

    # Grupo exibido no Swagger
    tags=["PDF"]
)


# Define endpoint POST.
#
# URL final:
# POST /pdf/upload_blob
@router.post("/upload_blob")
async def upload_pdf_blob(

    # Objeto Request contendo toda requisição HTTP.
    request: Request,

    # Arquivo obrigatório.
    #
    # File(...) => obrigatório.
    file: UploadFile = File(...),

    # Campos obrigatórios do formulário.
    cd_paciente: str = Form(...),
    cd_atendimento: str = Form(...),
    nm_paciente: str = Form(...),

    # Campos opcionais.
    #
    # Form(None) => não obrigatório.
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

    # Bloco de tratamento de erros.
    try:

        # Obtém parâmetro da URL.
        #
        # Exemplo:
        # /pdf/upload_blob?id=10
        #
        # Resultado:
        # id_param = "10"
        id_param = request.query_params.get("id")

        # Verifica se o usuário enviou o parâmetro.
        if not id_param:

            # Retorna erro HTTP 400.
            raise HTTPException(
                status_code=400,
                detail="Parâmetro 'id' obrigatório"
            )

        # Tenta converter o parâmetro para inteiro.
        try:

            documento_id = int(id_param)

        # Caso não seja número.
        except ValueError as exc:

            raise HTTPException(
                status_code=400,
                detail="Parâmetro 'id' inválido"
            ) from exc

        # Lê todo conteúdo do PDF enviado.
        #
        # Retorna bytes.
        #
        # Exemplo:
        # b'%PDF-1.7....'
        content = await file.read()
        print("PDF recebido")
        print("Documento clinico:", documento_id)
        print("Paciente:", cd_paciente)
        # Chama camada Service.
        #
        # O Controller apenas recebe os dados.
        #
        # Toda regra de negócio deve estar na Service.
        result = upload_pdf(

                
            # Id do documento
            documento_id=documento_id,

            # Conteúdo binário do PDF
            content=content,

            # Metadados do documento
            data={

                "cd_paciente": cd_paciente,
                "cd_atendimento": cd_atendimento,
                "nm_paciente": nm_paciente,
                "cd_objeto": cd_objeto,
                "cd_setor": cd_setor,
                "nm_setor": nm_setor,
                "cd_leito": cd_leito,
                "ds_leito": ds_leito,
                "cd_tipo_documento": cd_tipo_documento,
                "ds_tipo_documento": ds_tipo_documento,
                "nm_documento": nm_documento,
                "dh_fechamento": dh_fechamento,
                "dh_impresso": dh_impresso,
                "tp_status": tp_status,
            },
        )

        # Retorna resposta JSON para o cliente.
        return {

            # Mensagem de sucesso.
            "message": result["message"],

            # Id salvo.
            "id": result["id"],

            # Tamanho do arquivo.
            "size": result["size"],

            # True se atualizou.
            # False se inseriu.
            "updated": result["updated"],
        }

    # Captura erros de validação vindos da Service.
    except ValueError as exc:

        # Define status HTTP baseado na mensagem.
        #
        # Exemplo:
        # "PDF excede tamanho máximo"
        # => 413
        status_code = (
            413
            if "tamanho máximo" in str(exc).lower()
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        ) from exc

    # Captura erros internos da aplicação.
    except RuntimeError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc

    # Repassa erros HTTP já tratados.
    except HTTPException:
        raise


# Endpoint GET.
#
# Exemplo:
# GET /pdf/15
@router.get("/{id}")
def obter_pdf(id: int):

    try:

        # Busca PDF através da camada Service.
        pdf = get_pdf_service(id)

        # Caso não encontre registro.
        if not pdf:

            raise HTTPException(
                status_code=404,
                detail="PDF não encontrado"
            )

        # Retorna arquivo PDF para o navegador.
        return StreamingResponse(

            # Converte bytes para stream.
            #
            # O navegador entende como arquivo.
            BytesIO(pdf.pdf_blob),

            # MIME Type.
            #
            # Informa ao navegador que é PDF.
            media_type="application/pdf",

            # Cabeçalhos HTTP.
            headers={

                # inline:
                # abre diretamente no navegador.
                #
                # attachment:
                # forçaria download.
                "Content-Disposition":
                    f'inline; filename="{pdf.nm_documento}"'
            }
        )

    # Repassa exceções HTTP.
    except HTTPException:
        raise