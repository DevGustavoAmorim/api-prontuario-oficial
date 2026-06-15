###########################################################################################
#### Cadastrar papéis, empresas e usuários (Seed - Multiempresa 20 Usuários)
###########################################################################################
from db.session import SessionLocal
from app.models.usuario_models import Usuario, VinculoUsuarioEmpresa
from app.models.papel_models import Papel
from app.models.empresa_models import Empresa 
from app.core.security import gerar_hash_senha

def criar_usuarios():
    db = SessionLocal()

    print("\n--- Iniciando a Semeadura de Dados (Seed) ---")

    # 1. Garante que os papéis existam no banco
    papeis_iniciais = ["SYS", "MASTER", "SUPERVISOR", "USUARIO_UNIDADE"]
    for i, nome_papel in enumerate(papeis_iniciais, start=1):
        papel_existe = db.query(Papel).filter(Papel.id == i).first()
        if not papel_existe:
            db.add(Papel(id=i, nome=nome_papel))
    db.commit()
    print("✓ Papéis verificados/criados.")

    # 2. Garante as empresas para o ecossistema multiempresa
    empresas_iniciais = [
        {"cd_empresa": "1", "nome": "Hospital Central", "cnpj": "11.111.111/0001-11"},
        {"cd_empresa": "2", "nome": "Santa Casa de Misericórdia", "cnpj": "22.222.222/0001-22"},
        {"cd_empresa": "3", "nome": "Clínica Geral Avançada", "cnpj": "33.333.333/0001-33"}
    ]
    for emp in empresas_iniciais:
        empresa_existe = db.query(Empresa).filter(Empresa.cd_empresa == emp["cd_empresa"]).first()
        if not empresa_existe:
            db.add(Empresa(cd_empresa=emp["cd_empresa"], nome=emp["nome"], cnpj=emp["cnpj"]))
    db.commit()
    print("✓ Empresas verificadas/criadas.")

    # 3. Lista expandida com os 20 usuários
    usuarios = [
        {"nome": "Usuario SYS", "email": "sys@hospital.com", "senha": "123456", "papel_id": 1, "cd_empresa": None},
        {"nome": "Usuario MASTER", "email": "master@hospital.com", "senha": "123456", "papel_id": 2, "cd_empresa": "1"},
        {"nome": "Usuario SUPERVISOR", "email": "supervisor@hospital.com", "senha": "123456", "papel_id": 3, "cd_empresa": "1"},
        {"nome": "Usuario UNIDADE", "email": "unidade@hospital.com", "senha": "123456", "papel_id": 4, "cd_empresa": "1"},
        {"nome": "Gustavo Amorim", "email": "gustavo@teste.com.br", "senha": "123456", "papel_id": 2, "cd_empresa": "1"},
        {"nome": "Médico Plantonista", "email": "medico@hospital.com", "senha": "123456", "papel_id": 4, "cd_empresa": "1"},
        {"nome": "Rodrigo Silva", "email": "rodrigo.silva54@teste.com.br", "senha": "123456", "papel_id": 3, "cd_empresa": "2"},
        {"nome": "Ana Costa", "email": "ana.costa23@hospital.com", "senha": "123456", "papel_id": 2, "cd_empresa": "3"},
        {"nome": "Carlos Pereira", "email": "carlos.pereira88@saude.org", "senha": "123456", "papel_id": 4, "cd_empresa": "1"},
        {"nome": "Maria Oliveira", "email": "maria.oliveira12@clinica.med.br", "senha": "123456", "papel_id": 3, "cd_empresa": "3"},
        {"nome": "Juliana Souza", "email": "juliana.souza45@hospital.com", "senha": "123456", "papel_id": 4, "cd_empresa": "2"},
        {"nome": "Fernando Lima", "email": "fernando.lima71@teste.com.br", "senha": "123456", "papel_id": 2, "cd_empresa": "2"},
        {"nome": "Camila Carvalho", "email": "camila.carvalho19@saude.org", "senha": "123456", "papel_id": 4, "cd_empresa": "3"},
        {"nome": "Larissa Almeida", "email": "larissa.almeida33@clinica.med.br", "senha": "123456", "papel_id": 3, "cd_empresa": "1"},
        {"nome": "Ricardo Ribeiro", "email": "ricardo.ribeiro92@teste.com.br", "senha": "123456", "papel_id": 4, "cd_empresa": "2"},
        {"nome": "Beatriz Santos", "email": "beatriz.santos60@hospital.com", "senha": "123456", "papel_id": 2, "cd_empresa": "1"},
        {"nome": "Gabriel Costa", "email": "gabriel.costa74@saude.org", "senha": "123456", "papel_id": 3, "cd_empresa": "2"},
        {"nome": "Amanda Lima", "email": "amanda.lima15@clinica.med.br", "senha": "123456", "papel_id": 4, "cd_empresa": "3"},
        {"nome": "Mateus Pereira", "email": "mateus.pereira28@hospital.com", "senha": "123456", "papel_id": 3, "cd_empresa": "1"},
        {"nome": "Leticia Souza", "email": "leticia.souza81@saude.org", "senha": "123456", "papel_id": 4, "cd_empresa": "2"}
    ]

    # 4. Força a inserção de todos os usuários mapeados
    for dados in usuarios:
        # Garante a exclusão para não dar conflito se sobrou lixo de memória
        existe = db.query(Usuario).filter(Usuario.email == dados["email"]).first()
        if existe:
            db.delete(existe)
            db.flush()

        # Passo A: Cria o usuário cadastral básico
        novo_usuario = Usuario(
            nome=dados["nome"],
            email=dados["email"],
            senha=gerar_hash_senha(str(dados["senha"]).strip())
        )
        db.add(novo_usuario)
        db.flush()  # Gera o ID na memória temporária do SQLite

        # Passo B: Cria o vínculo multiempresa na tabela intermediária
        novo_vinculo = VinculoUsuarioEmpresa(
            usuario_id=novo_usuario.id,
            empresa_id=dados["cd_empresa"],
            papel_id=dados["papel_id"]
        )
        db.add(novo_vinculo)
        print(f"  -> Usuário [{dados['email']}] semeado com sucesso.")

    db.commit()
    db.close()
    print("\n🎉 Todos os 20 usuários e seus vínculos foram inseridos com sucesso!")
