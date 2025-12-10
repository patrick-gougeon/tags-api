import pandas as pd
# Importamos o 'app' (que já sabe qual banco usar pelo .env)
# e o 'db' (que é a ferramenta de conexão)
from app import app
from models import db, EspecialidadeModel, MedicoModel, ResponsavelModel, PlanoModel, CirurgiaModel

class ProcessadorExcel:
    
    def __init__(self):
        # Mapa: Nome da aba no Excel -> Tabela no Banco de Dados
        self.mapa_tabelas = {
            'Médicos': MedicoModel,
            'Responsáveis': ResponsavelModel,
            'Planos': PlanoModel,
            'Especialidades': EspecialidadeModel,
            'Cirurgias': CirurgiaModel
        }

        # Colunas que vamos ler do Excel
        self.campos = {
            'Médicos': ['Nome', 'Especialidade', 'Tipo'],
            'Responsáveis': ['Nome', 'Email', 'Telefone'],
            'Planos': ['Nome', 'Sigla'],
            'Especialidades': ['Nome', 'Descrição'],
            'Cirurgias': ['Nome', 'Especialidade Relacionada']
        }

    def processar_planilha(self, excel_caminho, planilha_nome):
        # Lê o Excel
        df = pd.read_excel(
            excel_caminho, 
            sheet_name=planilha_nome, 
            skiprows=1, 
            usecols=self.campos[planilha_nome]
        )
        
        # TRUQUE IMPORTANTE:
        # O banco usa minúsculo ('nome'), o Excel usa Maiúsculo ('Nome').
        # Esse comando converte todos os cabeçalhos do Excel para minúsculo automaticamente.
        df.columns = df.columns.str.lower()
        
        # Correção específica para chaves estrangeiras que têm nomes diferentes
        # Se existir coluna 'especialidade', renomeia para 'id_especialidade'
        # Se existir coluna 'especialidade relacionada', renomeia para 'id_especialidade'
        df = df.rename(columns={
            'especialidade': 'id_especialidade',
            'especialidade relacionada': 'id_especialidade',
            'descrição': 'descricao' # Remove o acento se houver
        })

        return df.to_dict('records')
    
    def salvar_no_banco(self, dados, Modelo):
        print(f"--- Inserindo {len(dados)} registros em {Modelo.__tablename__} ---")
        sucessos = 0
        
        for item in dados:
            try:
                # Cria o objeto do banco (Ex: MedicoModel) preenchendo com os dados do item
                novo_objeto = Modelo(**item)
                
                # Adiciona na sessão
                db.session.add(novo_objeto)
                sucessos += 1
            except Exception as e:
                print(f"Erro ao preparar item: {e}")

        # Tenta salvar tudo de uma vez (Commit)
        try:
            db.session.commit()
            print(f"Sucesso! {sucessos} itens salvos no banco.\n")
        except Exception as e:
            db.session.rollback() # Cancela se der erro
            print(f"Erro grave ao salvar no banco: {e}\n")

    def executar(self, excel_caminho):
        # Ordem de inserção para evitar erros (primeiro as tabelas independentes)
        ordem = ['Especialidades', 'Planos', 'Responsáveis', 'Médicos', 'Cirurgias']
        
        for aba in ordem:
            if aba in self.campos:
                dados = self.processar_planilha(excel_caminho, aba)
                if dados:
                    # Seleciona qual Modelo usar baseado no nome da aba
                    Modelo = self.mapa_tabelas[aba]
                    self.salvar_no_banco(dados, Modelo)

if __name__ == '__main__':
    # O PULO DO GATO:
    # "with app.app_context()" carrega as configurações do app.py (lendo o .env)
    # e permite mexer no banco sem precisar rodar o servidor do site.
    with app.app_context():
        processador = ProcessadorExcel() 
        processador.executar('template-upload-tags.xlsx')