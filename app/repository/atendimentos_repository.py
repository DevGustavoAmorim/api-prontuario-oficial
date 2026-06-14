from sqlalchemy.orm import Session

from app.models.pdf_model import PDFFile


class AtendimentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def listar_atendimentos(self):

        return (
            self.db.query(PDFFile)
            .order_by(
                PDFFile.dh_documento_fechado.desc()
            )
            .all()
        )

    def buscar_por_atendimento(
        self,
        cd_atendimento: str
    ):

        return (
            self.db.query(PDFFile)
            .filter(
                PDFFile.cd_atendimento == cd_atendimento
            )
            .order_by(
                PDFFile.dh_documento_fechado.desc()
            )
            .all()
        )