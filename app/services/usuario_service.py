# app/services/usuario_service.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.usuario_models import Usuario, VinculoUsuarioEmpresa  # 🔥 Importada a tabela intermediária
from app.models.papel_models import Papel
from app.core.security import gerar_hash_senha
from app.schemas.usuario_schema import UsuarioCreate

def criar_usuario_service(usuario: UsuarioCreate, db: Session, user_logado: Usuario):
    """
    Cria um novo usuário e estabelece seu vínculo na arquitetura Multiempresa.
    """
    # 1. VALIDAÇÃO PREVENTIVA: Impede a inserção se o e-mail já existir no banco
    email_existe = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if email_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está cadastrado no sistema."
        )

    # 2. CAPTURA O VÍNCULO ATUAL DO ADMINISTRADOR LOGADO
    vinculo_ativo = user_logado.vinculo_atual if user_logado.vinculo_atual else None
    if not vinculo_ativo:
        # Se for o SYS e não tiver empresa ativa, busca o vínculo de SYS dele
        sys_vinculo = next((v for v in user_logado.vinculos if v.papel.nome.upper().strip() == "SYS"), None)
        if sys_vinculo:
            vinculo_ativo = sys_vinculo
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="O usuário logado não possui nenhum vínculo ativo no sistema."
            )

    papel_logado = vinculo_ativo.papel.nome.upper().strip()
    empresa_logado_id = vinculo_ativo.empresa_id

    # Busca o papel que será atribuído ao novo usuário
    novo_usuario_papel = db.query(Papel).filter(Papel.id == usuario.papel_id).first()
    if not novo_usuario_papel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Papel inválido"
        )
    
    nome_novo_papel = novo_usuario_papel.nome.upper().strip().replace(" ", "_")

    # 3. VALIDAÇÃO DE PERMISSÕES ISOLADA
    if "SYS" in papel_logado:
        if nome_novo_papel not in ["SYS", "MASTER"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SYS só pode criar usuários com papel SYS ou MASTER"
            )

    elif "MASTER" in papel_logado:
        if nome_novo_papel not in ["MASTER", "SUPERVISOR", "USUARIO_UNIDADE"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="MASTER só pode criar usuários com papel MASTER, SUPERVISOR ou USUARIO_UNIDADE"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar usuários"
        )
    
    # 4. TRATAMENTO DA EMPRESA DESTINO (MECÂNICA MULTIEMPRESA)
    if "SYS" in papel_logado:
        if nome_novo_papel == "SYS":
            empresa_final = None  # Novo SYS fica sem empresa corporativa
        else:
            if not usuario.empresa_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuários com papel SYS precisam informar o 'empresa_id' ao criar um MASTER."
                )
            empresa_final = str(usuario.empresa_id).strip()
    else:
        # MASTER herda obrigatoriamente a empresa da sessão ativa dele
        empresa_final = empresa_logado_id

    # 5. GRAVAÇÃO EM DUAS ETAPAS (TRANSAÇÃO SEGURA COM FLUSH)
    try:
        # Etapa A: Salva na tabela cadastral de usuários
        novo = Usuario(
            nome=usuario.nome,
            email=usuario.email,
            senha=gerar_hash_senha(usuario.senha)
        )
        db.add(novo)
        db.flush()  # Gera temporariamente o ID do novo usuário no SQLite

        # Etapa B: Cria a regra de acesso vinculando o papel e a empresa
        novo_vinculo = VinculoUsuarioEmpresa(
            usuario_id=novo.id,
            empresa_id=empresa_final,
            papel_id=usuario.papel_id
        )
        db.add(novo_vinculo)
        
        db.commit()      # Grava as duas tabelas juntas no banco de dados
        db.refresh(novo) # Atualiza o objeto para o Pydantic Response renderizar
        return novo

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está cadastrado no sistema."
        )
