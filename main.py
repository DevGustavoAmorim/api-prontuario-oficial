from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

from app.controller.pdf_controller import router as pdf_router
from app.controller.pacientes_controller import router as pacientes_router
from app.controller.atendimentos_controller import router as atendimentos_router

from app.controller.auth_controller import router_auth as auth_router  

from app.controller.empresas_controller import router as empresa_router

from app.controller.papel_controller import router as roles_router

from app.controller.usuario_empresa_controller import router as usuario_empresa_router

from app.controller.usuarios_controller import router as usuarios_router
from app.controller.usuarios_controller import router as usuarios_router

from db.base import Base
from db.session import engine

# Cria a aplicação FastAPI
app = FastAPI(
    title="Hospital API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React/Vite
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(pdf_router)
app.include_router(pacientes_router)
app.include_router(atendimentos_router)

app.include_router(empresa_router)
app.include_router(roles_router)
app.include_router(usuarios_router)
app.include_router(usuario_empresa_router)
app.include_router(auth_router)
app.include_router(usuarios_router)

# Cria as tabelas no banco (somente se não existirem)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"status": "online"}