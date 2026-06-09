from pydantic import BaseModel

class PDFResponse(BaseModel):
    id: int
    filename: str
    cd_paciente:str
    cd_atendimento:str
    class Config:
        orm_mode = True
