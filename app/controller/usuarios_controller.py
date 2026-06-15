from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db

from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse,  EmpresasDoUsuarioResponse
from app.services.usuario_service import criar_usuario_service

# Importação dos modelos atualizados na arquitetura Multiempresa
from app.models.usuario_models import Usuario, VinculoUsuarioEmpresa  # 🔥 Atualizado
from app.models.papel_models import Papel

from app.dependencias.auth_dependencias import get_current_user

from typing import List

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(get_current_user)
):
    # 1. Captura o vínculo ativo do usuário administrativo logado nesta sessão
    vinculo_usuario_logado_ativo = usuario_logado.vinculos[0] if usuario_logado.vinculos else None
    if not vinculo_usuario_logado_ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O usuário logado não possui vínculos ativos no sistema."
        )

    papel_usuario_logado = vinculo_usuario_logado_ativo.papel.nome.upper().strip()
    cd_empresa_usuario_logado = vinculo_usuario_logado_ativo.empresa_id

    # 2. Se o usuário logado for SYS, ele possui "PASS" livre e visualiza absolutamente tudo
    if "SYS" in papel_usuario_logado:
        return db.query(Usuario).all()

    # 3. Se for MASTER, aplica a regra restritiva de segurança institucional
    elif "MASTER" in papel_usuario_logado:
        return (
            db.query(Usuario)
            # Une a tabela de usuários com a tabela intermediária de vínculos
            .join(VinculoUsuarioEmpresa, Usuario.id == VinculoUsuarioEmpresa.usuario_id)
            # Une com a tabela de papéis para podermos filtrar pelo nome textual do cargo
            .join(Papel, VinculoUsuarioEmpresa.papel_id == Papel.id)
            # Filtro A: Garante que os listados pertençam à MESMA empresa do MASTER
            .filter(VinculoUsuarioEmpresa.empresa_id == cd_empresa_usuario_logado)
            # Filtro B: Restringe a visualização apenas para os cargos permitidos na hierarquia
            .filter(Papel.nome.in_(["MASTER", "SUPERVISOR", "USUARIO_UNIDADE"]))
            .all()
        )
    
    # Demais papéis não listam usuários
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seu nível de acesso não permite listar usuários do sistema."
        )

# Importe o novo schema no topo do seu app/api/usuarios_api.py

# Adicione o response_model na assinatura da rota:
@router.get("/{usuario_id}/empresas", response_model=List[EmpresasDoUsuarioResponse])
def listar_empresas(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    # Mapeia exatamente as chaves do seu novo schema
    return [
        {
            "id_vinculo": v.id,
            "papel_id": v.papel_id,
            "papel_nome": v.papel.nome,
            "empresa": v.empresa
        }
        for v in usuario.vinculos if v.empresa is not None
    ]

@router.post("/CriarUsuario", response_model=UsuarioResponse)
def criar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    user_logado=Depends(get_current_user)
):
    return criar_usuario_service(
        usuario=usuario,
        db=db,
        user_logado=user_logado
    )
