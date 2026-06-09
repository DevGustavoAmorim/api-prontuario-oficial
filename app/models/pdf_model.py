from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from db.base import Base

class PDFFile(Base):
    __tablename__ = "atendimento"

    id = Column(Integer, primary_key=True, index=True)  # cd_documento_clinico
    cd_paciente = Column(String, nullable=False)
    cd_atendimento = Column(String, nullable=True)
    nm_paciente = Column(String, nullable=False)

    cd_objeto = Column(String, nullable=True)
    cd_setor = Column(String, nullable=True)
    nm_setor = Column(String, nullable=True)
    cd_leito = Column(String, nullable=True)
    ds_leito = Column(String, nullable=True)
    cd_tipo_documento = Column(String, nullable=True)
    ds_tipo_documento = Column(String, nullable=True)
    nm_documento = Column(String, nullable=True)
    tp_status = Column(String, nullable=True)
    dh_documento_fechado = Column(DateTime, nullable=True)
    dh_documento_importado = Column(DateTime, nullable=True)

    pdf_blob = Column(LargeBinary, nullable=False)
