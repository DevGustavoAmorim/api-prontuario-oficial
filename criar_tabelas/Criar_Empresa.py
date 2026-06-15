###########################################################################################
#### Cadastrar empresas 
###########################################################################################
from app.database.connection import SessionLocal
from app.models.empresa_models import Empresa


def criar_empresas():
    db = SessionLocal()

    empresas = [
        {
            "cd_empresa": "1001",
            "nome": "Hospital Central",
            "cnpj": "11111111000111"
        },
        {
            "cd_empresa": "1002",
            "nome": "Hospital Zona Sul",
            "cnpj": "22222222000122"
        },
        {
            "cd_empresa": "1003",
            "nome": "Hospital Zona Norte",
            "cnpj": "33333333000133"
        }
    ]

    for dados in empresas:
        existe = db.query(Empresa).filter(
            Empresa.cd_empresa == dados["cd_empresa"]
        ).first()

        if not existe:

            empresa = Empresa(
                cd_empresa=dados["cd_empresa"],
                nome=dados["nome"],
                cnpj=dados["cnpj"]
            )

            db.add(empresa)

    db.commit()
    db.close()

    print("Empresas criadas com sucesso!")