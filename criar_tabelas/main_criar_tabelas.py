import os
from db.session import engine
from db.base import Base

# 1. Força a limpeza completa de qualquer tabela "fantasma" que tenha ficado presa na memória do Python
Base.metadata.clear()

# 2. IMPORTANTE: Importa os modelos ATUALIZADOS para remapear os metadados do zero
from app.models.empresa_models import Empresa
from app.models.papel_models import Papel
from app.models.usuario_models import Usuario, VinculoUsuarioEmpresa

# 3. IMPORTAÇÃO ADICIONADA: Traz a função de sementes (seed) para o arquivo principal
from criar_tabelas.Criar_Usuarios import criar_usuarios

def excluir_db():
    if os.path.exists("prontuario_distribuido.db"):
        try:
            os.remove("prontuario_distribuido.db")
            print("Banco de dados físico excluído com sucesso!")
        except PermissionError:
            print("⚠️ AVISO: O arquivo do banco está travado por outro programa (API rodando ou visualizador de banco aberto). Feche-os para aplicar as alterações físicas.")
    else:
        print("Banco de dados não encontrado para exclusão.")

if __name__ == "__main__":
    # Passo A: Deleta o arquivo físico antigo do disco
    excluir_db()
    
    # Passo B: Cria as tabelas do zero usando a estrutura Multiempresa atualizada e sem colunas fantasmas
    Base.metadata.create_all(bind=engine)
    print("Tabelas físicas recriadas com sucesso no banco de dados!")
    
    # 🔥 CHAMADA ADICIONADA: Executa a criação dos 20 usuários e seus vínculos no banco de dados
    criar_usuarios()
