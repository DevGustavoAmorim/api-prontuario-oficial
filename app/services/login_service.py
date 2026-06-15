from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.usuario_models import Usuario
from app.auth.auth import verify_password, create_access_token


def login_service(email: str, senha: str, db: Session):

    usuario = db.query(Usuario).filter(
        Usuario.email == email
    ).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    if not verify_password(senha, usuario.senha):
        raise HTTPException(status_code=401, detail="Senha inválida")

    token = create_access_token({
        "user_id": usuario.id,
        "email": usuario.email,
        "papel_id": usuario.papel_id
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }