from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db

from app.models.usuario_models import Usuario, VinculoUsuarioEmpresa
from app.models.empresa_models import Empresa
from app.models.papel_models import Papel

from app.dependencias.auth_dependencias import get_current_user
from pydantic import BaseModel

class NovoVinculoInput(BaseModel):
    usuario_id: int
    cd_empresa: str
    papel_id: int 

router = APIRouter(
    prefix="/usuario-empresa",
    tags=["Vínculos Multiempresa"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vincular_usuario_empresa(
    usuario_empresa: NovoVinculoInput,
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(get_current_user)
):
    """
    Cria um novo vínculo de acesso associando um usuário a uma empresa com um papel específico.

    Esta rota implementa as travas de governança multiempresa do sistema, restringindo 
    a criação de novos vínculos de acordo com o nível de privilégio do usuário autenticado.

    Args:
        usuario_empresa (NovoVinculoInput): Dados de entrada contendo as chaves 
            estrangeiras do usuário, empresa e papel.
        db (Session): Sessão ativa de conexão com o banco de dados.
        usuario_logado (Usuario): Entidade do usuário administrativo realizando a ação.

    Returns:
        dict: Detalhes textuais confirmando o sucesso do vínculo gerado no banco.

    Raises:
        HTTPException (403): Caso o usuário logado não tenha privilégios suficientes, 
            tente vincular em uma empresa diferente da sua (para MASTER) ou tente 
            atribuir um papel acima de sua hierarquia.
        HTTPException (404): Se o usuário, empresa ou papel informados não existirem.
        HTTPException (400): Se o vínculo exato já estiver cadastrado no banco.
    """
    # Etapa 1: Resgate do Contexto Administrativo
    # Verifica o papel do usuário logado e seu vínculo ativo para aplicar as regras de governança multiempresa
    vinculo_ativo = usuario_logado.vinculo_atual if usuario_logado.vinculo_atual else None
    is_sys = any(v.papel.nome.upper().strip() == "SYS" for v in usuario_logado.vinculos if v.papel)

    # Se não for SYS and não tiver vínculo ativo, bloqueia o acesso imediatamente
    if not is_sys and not vinculo_ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seu usuário não possui nenhum vínculo ativo no sistema."
        )

    # Retorna o papel e empresa do vínculo ativo para as regras de governança, ou SYS se for o caso
    papel_logado = "SYS" if is_sys else vinculo_ativo.papel.nome.upper().strip()
    empresa_logado_id = None if is_sys else vinculo_ativo.empresa_id

    # Etapa 2: Controle de Escopo Territorial (Trava Institucional do MASTER)
    # Se usuário é MASTER, só pode vincular dentro da própria empresa.
    # Se usuário é SYS, pode vincular em qualquer empresa sem restrição.
    if "MASTER" in papel_logado:
        if str(usuario_empresa.cd_empresa).strip() != str(empresa_logado_id).strip():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Um administrador MASTER só pode vincular usuários dentro da sua própria empresa."
            )
    
    # Se não for MASTER e não for SYS, não pode vincular em nenhuma empresa (pois não tem visão global)
    # Bloqueia explicitamente papéis como SUPERVISOR e USUARIO_UNIDADE de criarem ou vincularem contas
    elif "SYS" not in papel_logado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seu nível de acesso não permite vincular usuários a empresas."
        )

    # Etapa 3: Validação de Chaves Estrangeiras (Existência no Banco)
    # Dados do destino do vinculo: usuário, empresa e papel
    # Valida se o usuário destino existe
    user = db.query(Usuario).filter(Usuario.id == usuario_empresa.usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário destino não encontrado.")

    emp = db.query(Empresa).filter(Empresa.cd_empresa == usuario_empresa.cd_empresa).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empresa destino não encontrada.")

    ppl = db.query(Papel).filter(Papel.id == usuario_empresa.papel_id).first()
    if not ppl:
        raise HTTPException(status_code=404, detail="Papel informado é inválido.")

    # Limpeza e padronização do nome do papel para comparação hierárquica
    nome_novo_papel = ppl.nome.upper().strip().replace(" ", "_")

    # Etapa 4: Validação de Hierarquia Funcional Restrita
    # Verifica o papel do criador logado e restringe rigidamente quais cargos ele pode conceder no destino
    # Se o papel criador for SYS, ele só possui autorização para criar ou vincular perfis do tipo MASTER ou outro SYS
    if "SYS" in papel_logado and nome_novo_papel not in ["SYS", "MASTER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SYS só pode criar ou vincular usuários com papel SYS ou MASTER."
        )

    # Se o papel criador for MASTER, ele só possui autorização para criar ou vincular perfis do tipo SUPERVISOR ou USUARIO_UNIDADE
    elif "MASTER" in papel_logado and nome_novo_papel not in ["SUPERVISOR", "USUARIO_UNIDADE"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MASTER só pode criar ou vincular usuários com papel SUPERVISOR ou USUARIO_UNIDADE."
        )

    # Etapa 5: Interceptação Preventiva de Duplicidade
    v_existe = db.query(VinculoUsuarioEmpresa).filter(
        VinculoUsuarioEmpresa.usuario_id == usuario_empresa.usuario_id,
        VinculoUsuarioEmpresa.empresa_id == usuario_empresa.cd_empresa,
        VinculoUsuarioEmpresa.papel_id == usuario_empresa.papel_id
    ).first()

    if v_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este usuário já possui este papel vinculado nesta empresa."
        )

    # Etapa 6: Persistência Física do Vínculo
    novo_vinculo = VinculoUsuarioEmpresa(
        usuario_id=usuario_empresa.usuario_id,
        empresa_id=str(usuario_empresa.cd_empresa).strip(),
        papel_id=usuario_empresa.papel_id
    )

    db.add(novo_vinculo)
    db.commit()
    db.refresh(novo_vinculo)

    return {
        "id_vinculo": novo_vinculo.id,
        "usuario": user.nome,
        "empresa": emp.nome,
        "papel": ppl.nome,
        "message": f"Usuário vinculado com sucesso sob a governança de {papel_logado}!"
    }
