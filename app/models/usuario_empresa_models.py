from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint

from app.database.connection import Base


class UsuarioEmpresa(Base):
    __tablename__ = "usuario_empresa"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    cd_empresa = Column(
        String(20),
        ForeignKey("empresas.cd_empresa"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "usuario_id",
            "cd_empresa",
            name="uq_usuario_empresa"
        ),
    )