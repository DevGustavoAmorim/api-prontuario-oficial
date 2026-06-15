from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.usuario_empresa_models import UsuarioEmpresa
from app.models.empresa_models import Empresa

def vincular_usuario_empresa_service(
    usuario_empresa,
    db: Session
    ):
    
    existe = db.query(UsuarioEmpresa).filter(
        UsuarioEmpresa.usuario_id == usuario_empresa.usuario_id,
        UsuarioEmpresa.cd_empresa == usuario_empresa.cd_empresa
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Usuário já vinculado à empresa"
        )

    vinculo = UsuarioEmpresa(
        usuario_id=usuario_empresa.usuario_id,
        cd_empresa=usuario_empresa.cd_empresa
    )

    db.add(vinculo)
    db.commit()
    db.refresh(vinculo)

    return vinculo

def listar_empresas_usuario(usuario, db):

    # SYS vê tudo
    if usuario.papel.nome == "SYS":
        return db.query(Empresa).all()

    # demais usuários seguem vínculo
    return (
        db.query(Empresa)
        .join(UsuarioEmpresa, Empresa.cd_empresa == UsuarioEmpresa.cd_empresa)
        .filter(UsuarioEmpresa.usuario_id == usuario.id)
        .all()
    )

def obter_empresas_usuario(usuario, db):

    if usuario.papel.nome == "SYS":
        return None

    return [
        v.cd_empresa
        for v in db.query(UsuarioEmpresa)
                    .filter(UsuarioEmpresa.usuario_id == usuario.id)
                    .all()
    ]