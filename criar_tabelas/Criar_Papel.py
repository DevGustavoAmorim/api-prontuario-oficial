###########################################################################################
#### Cadastrar Papeis
###########################################################################################

from app.database.connection import SessionLocal
from app.models.papel_models import Papel

def criar_papeis():
    db = SessionLocal()

    papeis = [
        "SYS",
        "MASTER",
        "SUPERVISOR",
        "USUARIO_UNIDADE"
    ]

    for nome in papeis:

        existe = db.query(Papel).filter(
            Papel.nome == nome
        ).first()

        if not existe:
            db.add(
                Papel(nome=nome)
            )

    db.commit()
    db.close()

    print("Papeis cadastrados com sucesso!")

