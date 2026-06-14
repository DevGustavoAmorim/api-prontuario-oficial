# PROF-API

API REST desenvolvida com FastAPI para gerenciar operações de prontuário e serviços profissionais.

## Descrição

Esta API foi construída usando FastAPI, oferecendo rotas rápidas e documentação automática via Swagger e ReDoc.

## Tecnologias

- Python
- FastAPI
- Uvicorn

## Requisitos

- Python 3.11+
- pip

## Instalação

1. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate       # Windows
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Executando a API

```bash
uvicorn main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`.




