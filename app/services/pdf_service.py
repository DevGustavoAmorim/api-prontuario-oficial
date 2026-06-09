from db.session import SessionLocal
from app.models.pdf_model import PDFFile

def save_pdf(filename: str, content: bytes, tipo: str):
    print(f"[save_pdf] Recebido: {filename} | Tipo: {tipo} | Tamanho: {len(content)} bytes")
    ...
    try:
        db = SessionLocal()

        # Verifica se já existe um PDF com o mesmo nome e tipo
        existing = db.query(PDFFile).filter_by(filename=filename, tipo=tipo).first()
        if existing:
            print(f"[SKIP] PDF já existe: {filename} | Tipo: {tipo}")
            return {"id": existing.id, "filename": existing.filename, "tipo": existing.tipo}

        # Cria e salva novo PDF
        pdf = PDFFile(filename=filename, content=content, tipo=tipo)
        db.add(pdf)
        db.commit()
        db.refresh(pdf)
        print(f"[OK] PDF salvo no banco: {filename} | Tipo: {tipo}")
        return {"id": pdf.id, "filename": pdf.filename, "tipo": pdf.tipo}

    except Exception as e:
        print(f"[ERROR] Falha ao salvar PDF {filename}: {e}")
        return {"error": str(e)}
