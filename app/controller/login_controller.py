from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.login_schema import LoginRequest
from app.services.auth_service import login_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    return login_service(data.email, data.senha, db)