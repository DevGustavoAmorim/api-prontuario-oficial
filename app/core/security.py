# app/core/security.py
from pwdlib import PasswordHash

# Configuração moderna recomendada oficialmente pelo FastAPI
pwd_context = PasswordHash.recommended()

def gerar_hash_senha(senha: str) -> str:
    # Recebe a senha pura e gera o hash seguro automaticamente
    return pwd_context.hash(senha)

def verificar_senha(senha_puro: str, senha_hash: str) -> bool:
    # Compara a senha digitada com o hash salvo no banco
    return pwd_context.verify(senha_puro, senha_hash)
