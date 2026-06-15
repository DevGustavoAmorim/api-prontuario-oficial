from app.auth.auth import create_access_token
from app.auth.auth import verify_password, create_access_token

from db.session import get_db
from app.dependencias.auth_dependencias import get_current_user

from app.models.usuario_models import Usuario
from app.models.usuario_models import Usuario, VinculoUsuarioEmpresa
from app.models.usuario_models import VinculoUsuarioEmpresa

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import joinedload, Session
from sqlalchemy.orm import Session, joinedload

from typing import Optional

router_auth = APIRouter(tags=["Autenticação"])


@router_auth.post("/login")
def login(
    # OAuth2PasswordRequestForm captura automaticamente 'username' (e-mail) e 'password' no Swagger
    form_data: OAuth2PasswordRequestForm = Depends(),
    # Campo opcional para o usuário escolher qual hospital quer entrar (O SYS deixa em branco)
    empresa_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Realiza a autenticação do usuário e gera o Token JWT de sessão.
    Na arquitetura Multiempresa, você pode informar o 'empresa_id' do hospital desejado.
    """
    from sqlalchemy.orm import joinedload
    from app.models.usuario_models import VinculoUsuarioEmpresa

# ... dentro da sua função def login() ...

    # 1. Busca o usuário trazendo ANTECIPADAMENTE todos os vínculos e papéis em um único JOIN
    user = (
        db.query(Usuario)
        .options(
            joinedload(Usuario.vinculos).joinedload(VinculoUsuarioEmpresa.papel)
        )
        .filter(Usuario.email == form_data.username)
        .first()
    )
    
    if not user or not verify_password(form_data.password, user.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Este usuário está inativo no sistema."
        )

    # 2. VALIDAÇÃO DOS VÍCULOS MULTIEMPRESA
    # Descobre se o usuário possui o papel de suporte supremo (SYS)
    is_sys = any(v.papel.nome.upper().strip() == "SYS" for v in user.vinculos if v.papel)
    
    if not is_sys:
        if not empresa_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Por favor, selecione o 'empresa_id' do hospital que deseja acessar."
            )
            
        # Limpa possíveis espaços invisíveis que o Swagger possa mandar no formulário
        empresa_id_limpo = str(empresa_id).strip()

        # Varre os vínculos reais que vieram do banco de dados para validar o acesso
        vinculo_valido = False
        for v in user.vinculos:
            if v.empresa_id and str(v.empresa_id).strip() == empresa_id_limpo:
                vinculo_valido = True
                break

        if not vinculo_valido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui vínculo ou permissão nesta empresa."
            )

    # 3. GERAÇÃO DO PAYLOAD DO TOKEN
    token_data = {
        "user_id": user.id,
        "sub": user.email,
        "empresa_id": None if is_sys else str(empresa_id).strip()
    }

    token_acesso = create_access_token(data=token_data)

    return {
        "access_token": token_acesso,
        "token_type": "bearer"
    }


# Certifique-se de usar o mesmo roteador que você já registrou no main.py
# Se o seu roteador lá se chamar router_auth, use @router_auth.post
@router_auth.post("/trocar-empresa")
def trocar_empresa(
    empresa_id: str,
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(get_current_user)
):
    """
    Permite que um usuário Multiempresa mude o seu contexto de trabalho atual.
    Gera um novo Token JWT com o ID da nova empresa selecionada.
    """
    empresa_id_limpo = str(empresa_id).strip()

    # 1. Como o get_current_user já fechou a sessão, fazemos um rápido re-fetch 
    # para garantir que lemos todos os vínculos reais do usuário no banco
    user = (
        db.query(Usuario)
        .options(joinedload(Usuario.vinculos).joinedload(VinculoUsuarioEmpresa.papel))
        .filter(Usuario.id == usuario_logado.id)
        .first()
    )

    # 2. O usuário SYS não precisa de travas de vínculos, ele pode pular para qualquer empresa
    is_sys = any(v.papel.nome.upper().strip() == "SYS" for v in user.vinculos if v.papel)

    if not is_sys:
        # Varre a lista para garantir que ele realmente trabalha na empresa escolhida
        vinculo_valido = None
        for v in user.vinculos:
            if v.empresa_id and str(v.empresa_id).strip() == empresa_id_limpo:
                vinculo_valido = v
                break

        if not vinculo_valido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui vínculo de trabalho cadastrado nesta empresa."
            )

    # 3. Gera o novo Payload criptografado com o novo contexto de hospital
    token_data = {
        "user_id": user.id,
        "sub": user.email,
        "empresa_id": None if is_sys else empresa_id_limpo
    }

    novo_token_acesso = create_access_token(data=token_data)

    return {
        "access_token": novo_token_acesso,
        "token_type": "bearer",
        "message": f"Contexto alterado com sucesso para a empresa {empresa_id_limpo}."
    }
