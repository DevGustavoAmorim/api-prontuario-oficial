from datetime import datetime, timedelta
from pwdlib import PasswordHash
from jose import jwt, JWTError

SECRET_KEY = "hospital_secret_key"
ALGORITHM = "HS256"

# Configuração moderna recomendada pelo FastAPI
pwd_context = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# criar token
def create_access_token(data: dict, expires_minutes: int = 60):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except JWTError:
        return None