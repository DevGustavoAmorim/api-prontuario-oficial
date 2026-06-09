from sqlalchemy import Column, Integer, String
from db.base import Base

class Paciente(Base):
    __tablename__ = "pacientes"

    cd_paciente = Column(Integer, primary_key=True, index=True)
    nm_paciente = Column(String, nullable=False)
