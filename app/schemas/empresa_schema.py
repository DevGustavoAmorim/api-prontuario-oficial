from pydantic import BaseModel


class EmpresaCreate(BaseModel):
    """
    Params:
        cd_empresa: Código único da empresa.
        
        nome: Nome da empresa.
        
        cnpj: Cadastro Nacional da Pessoa Jurídica (CNPJ) da empresa.
        
    """
    cd_empresa: str
    nome: str
    cnpj: str


class EmpresaResponse(BaseModel):
    """
    Retorna os atributos de uma empresa, incluindo código da empresa, nome, CNPJ e status ativo.
    
    Aonde usar:
        - Na resposta de endpoints relacionados a empresas, como criação, listagem ou detalhes de uma empresa.
        - Para fornecer informações completas sobre uma empresa em respostas de API.
        - Em casos onde é necessário exibir os detalhes de uma empresa para os usuários ou para outras partes do sistema.

    Params:
        cd_empresa: Código único da empresa.
        
        nome: Nome da empresa.
        
        cnpj: Cadastro Nacional da Pessoa Jurídica (CNPJ) da empresa.
        
        ativo: Indica se a empresa está ativa ou inativa.
    """
    cd_empresa: str
    nome: str
    cnpj: str
    ativo: bool

    class Config:
        from_attributes = True