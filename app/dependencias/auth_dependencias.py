from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.auth import decode_token
from db.session import SessionLocal
# Importamos o VinculoUsuarioEmpresa para mapear o carregamento em cascata
from app.models.usuario_models import Usuario, VinculoUsuarioEmpresa 
from sqlalchemy.orm import joinedload

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Autentica e extrai o usuário atual a partir do token JWT enviado na requisição.

    Esta função atua como uma dependência do FastAPI. Ela intercepta o cabeçalho 
    'Authorization', valida a assinatura e a expiração do token Bearer, e 
    retorna o objeto do usuário autenticado diretamente do banco de dados.

    Args:
        credentials (HTTPAuthorizationCredentials): As credenciais extraídas 
            automaticamente do cabeçalho HTTP pelo FastAPI.

    Returns:
        Usuario: O objeto correspondente ao usuário autenticado, contendo 
            seus dados e o seu papel (role) associado à sessão atual.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido ou expirado"
        )

    user_id = payload.get("user_id")
    # Captura a empresa que este usuário escolheu trabalhar no momento do login
    empresa_sessao_id = payload.get("empresa_id") 

    db = SessionLocal()

    # Otimização de Query: Carrega o Usuário, seus Vínculos, os Papéis e as Empresas juntos
    user = (
        db.query(Usuario)
        .options(
            joinedload(Usuario.vinculos)
            .joinedload(VinculoUsuarioEmpresa.papel),
            joinedload(Usuario.vinculos)
            .joinedload(VinculoUsuarioEmpresa.empresa)
        )
        .filter(Usuario.id == user_id)
        .first()
    )

    db.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Usuário não encontrado"
        )

    # O GRANDE TRUQUE MULTIEMPRESA:
    # Varre a lista de vínculos do usuário e descobre qual linha bate com a empresa do Token
    vinculo_da_sessao = None
    if user.vinculos:
        # Garante que o ID da sessão vindo do Token JWT está limpo e é string
        empresa_token_limpo = str(empresa_sessao_id).strip() if empresa_sessao_id else None

        for v in user.vinculos:
            # Se for o usuário SYS, o papel_id ou nome do papel garante o acesso sem empresa rígida
            if v.papel and v.papel.nome.upper().strip() == "SYS":
                vinculo_da_sessao = v
                break
                
            # Para os demais usuários, limpa o ID do banco e compara como String pura
            if v.empresa_id:
                empresa_banco_limpo = str(v.empresa_id).strip()
                if empresa_banco_limpo == empresa_token_limpo:
                    vinculo_da_sessao = v
                    break

        # Se não for SYS e não achou um vínculo idêntico para a empresa do Token, barra o acesso
    is_sys = any(v.papel.nome.upper().strip() == "SYS" for v in user.vinculos if v.papel)
    if not vinculo_da_sessao and not is_sys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão para acessar esta empresa."
        )

    # 🔥 CORREÇÃO: Usamos um nome de atributo NOVO e exclusivo para a sessão atual.
    # Isso evita conflito com a lista nativa 'user.vinculos' do SQLAlchemy.
    user.vinculo_atual = vinculo_da_sessao

    return user
