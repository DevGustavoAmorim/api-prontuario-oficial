from typing import Optional

from sqlalchemy.orm import Session

from app.models.pdf_model import PDFFile


class PDFRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        documento_id: int
    ) -> Optional[PDFFile]:

        return (
            self.db.query(PDFFile)
            .filter(PDFFile.id == documento_id)
            .first()
        )

    def save(
        self,
        pdf: PDFFile
    ) -> PDFFile:

        self.db.add(pdf)
        self.db.flush()

        return pdf

    def update(
        self,
        pdf: PDFFile
    ) -> PDFFile:

        self.db.add(pdf)
        self.db.flush()

        return pdf

    def get_pdf_file(
        self,
        documento_id: int
    ) -> Optional[PDFFile]:

        return self.get_by_id(documento_id)