import re

def limpar_cnpj(cnpj: str) -> str:
    return re.sub(r"\D", "", cnpj)


def formatar_cnpj(cnpj: str) -> str:
    cnpj = limpar_cnpj(cnpj)

    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"