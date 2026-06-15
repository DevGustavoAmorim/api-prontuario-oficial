from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from app.models.empresa_models import Empresa
from app.schemas.empresa_schema import EmpresaCreate, EmpresaResponse
from app.services.empresa_service import criar_empresa_service
from typing import List
from db.session import SessionLocal
# Importamos a dependência de autenticação do usuário logado
from app.dependencias.auth_dependencias import get_current_user
from app.models.usuario_models import Usuario

router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"]
)


@router.get("/", response_model=List[EmpresaResponse])
def listar_empresas(
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(get_current_user)  # PROTEGIDO: Exige login ativo
):
    """
    Lista as empresas do sistema respeitando a governança de acesso.
    O SYS visualiza todas. O MASTER visualiza apenas a sua própria instituição.
    """
    # 1. Identifica o papel e a empresa da sessão ativa do usuário
    vinculo_ativo = usuario_logado.vinculo_atual if usuario_logado.vinculo_atual else None
    
    # Se ele não tem vínculo ativo mas possui a role de SYS listada, ele é o administrador supremo
    is_sys = any(v.papel.nome.upper().strip() == "SYS" for v in usuario_logado.vinculos if v.papel)

    if is_sys:
        # O SYS tem visão global do software inteiro
        return db.query(Empresa).all()

    if not vinculo_ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seu usuário não possui nenhum vínculo ativo no sistema."
        )

    papel_logado = vinculo_ativo.papel.nome.upper().strip()
    empresa_logado_id = vinculo_ativo.empresa_id

    # O MASTER só enxerga a própria empresa em que atua
    if "MASTER" in papel_logado:
        return db.query(Empresa).filter(Empresa.cd_empresa == empresa_logado_id).all()
    
    # Supervisores e Usuários comuns de Unidade não listam empresas
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seu nível de acesso não permite listar dados institucionais de empresas."
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_empresa(
    empresa: EmpresaCreate,
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(get_current_user)  # PROTEGIDO: Exige login ativo
):
    """
    Cadastra uma nova empresa no ecossistema do software.
    Operação restrita e exclusiva para usuários com privilégio de SYS.
    """
    # Verifica se a palavra 'SYS' está contida em algum dos papéis do usuário
    is_sys = any(v.papel.nome.upper().strip() == "SYS" for v in usuario_logado.vinculos if v.papel)

    if not is_sys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores do sistema (SYS) podem cadastrar novas empresas."
        )

    return criar_empresa_service(empresa, db)

@router.get("/minhas-empresas")
def listar_empresas_do_usuario_logado(
    usuario_logado: Usuario = Depends(get_current_user)
):
    """
    Retorna a lista de todas as empresas nas quais o usuário possui vínculo de acesso.
    Útil para preencher a lista suspensa (dropdown) no Frontend ou no momento do login.
    """
    # 1. Verifica se o usuário é o SYS supremo
    is_sys = any(v.papel.nome.upper().strip() == "SYS" for v in usuario_logado.vinculos if v.papel)

    if is_sys:
        # Regra de negócio: O SYS não tem empresa vinculada, ele tem acesso a TODAS.
        # Como o get_current_user fecha a sessão, abrimos uma rápida para o SYS trazer a lista global
        db = SessionLocal()
        todas_as_empresas = db.query(Empresa).all()
        db.close()
        
        return [
            {
                "cd_empresa": emp.cd_empresa,
                "nome_empresa": emp.nome,
                "papel_nome": "SYS"
            }
            for emp in todas_as_empresas
        ]

    # 2. Para os demais usuários (MASTER, SUPERVISOR, UNIDADE), varre os vínculos reais dele
    lista_empresas_acesso = []
    
    if usuario_logado.vinculos:
        for vinculo in usuario_logado.vinculos:
            # Garante que a linha de vínculo possui uma empresa mapeada válida
            if vinculo.empresa:
                lista_empresas_acesso.append({
                    "cd_empresa": vinculo.empresa.cd_empresa,
                    "nome_empresa": vinculo.empresa.nome,
                    "papel_id": vinculo.papel_id,
                    "papel_nome": vinculo.papel.nome if vinculo.papel else "N/A"
                })

    return lista_empresas_acesso
