from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controller.pdf_controller import router as pdf_router
from app.controller.pacientes_controller import router as pacientes_router
from app.controller.atendimentos_controller import router as atendimentos_router

from db.base import Base
from db.session import engine

# Cria a aplicação FastAPI
app = FastAPI(title="PDF BLOB API")

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

# Cria as tabelas no banco (somente se não existirem)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)