import pandas as pd
import numpy as np
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

        # Colunas esperadas no Excel
        self.campos = {
            'Médicos': ['Nome', 'Especialidade', 'Tipo'],
            'Responsáveis': ['Nome', 'Email', 'Telefone'],
            'Planos': ['Nome', 'Sigla'],
            'Especialidades': ['Nome', 'Descrição'],
            'Cirurgias': ['Nome', 'Especialidade Relacionada']
        }

    def _resolver_ids(self, df, modelo_referencia, col_excel, col_banco):
        """
        Converte nomes (texto) da planilha em IDs (inteiros) consultando o banco.
        """
        if col_excel not in df.columns:
            return df
            
        print(f"   -> Buscando IDs para coluna '{col_excel}' na tabela {modelo_referencia.__tablename__}...")

        # Busca todos os pares (nome, id) do banco
        registros = modelo_referencia.query.with_entities(modelo_referencia.nome, modelo_referencia.id).all()
        
        # Cria mapa: {'cardiologia': 1, 'pediatria': 2}
        mapa_ids = {str(r.nome).lower().strip(): r.id for r in registros}
        
        # Mapeia os valores. Use o map para substituir pelo ID
        df[col_banco] = df[col_excel].astype(str).str.lower().str.strip().map(mapa_ids)
        
        # Remove a coluna original de texto
        df = df.drop(columns=[col_excel])
        
        return df

    def processar_planilha(self, excel_caminho, planilha_nome):
        print(f"Lendo aba: {planilha_nome}...")
        
        df = pd.read_excel(
            excel_caminho, 
            sheet_name=planilha_nome, 
            skiprows=1, 
            usecols=self.campos[planilha_nome]
        )
        
        # Converte cabeçalhos para minúsculo
        df.columns = df.columns.str.lower()
        
        # --- TRATAMENTO 1: NOMES EM MINÚSCULO ---
        if 'nome' in df.columns:
            # Converte para string, joga pra minusculo e remove espaços nas pontas
            df['nome'] = df['nome'].astype(str).str.lower().str.strip()

        # --- TRATAMENTO 2: LIMPEZA DE TELEFONE (APENAS NÚMEROS) ---
        if 'telefone' in df.columns:
            # Regex r'\D' significa "Qualquer coisa que NÃO seja um dígito (0-9)"
            # Substituímos tudo que não é dígito por vazio ''
            df['telefone'] = df['telefone'].astype(str).str.replace(r'\D', '', regex=True)

        # --- RENOMEAÇÕES ---
        df = df.rename(columns={
            'descrição': 'descricao',
            'especialidade relacionada': 'especialidade_temp' 
        })

        # --- TRATAMENTO DE FK (Foreign Keys) ---
        if planilha_nome == 'Médicos':
            df = self._resolver_ids(df, EspecialidadeModel, 'especialidade', 'id_especialidade')

        elif planilha_nome == 'Cirurgias':
            col_busca = 'especialidade_temp' if 'especialidade_temp' in df.columns else 'especialidade relacionada'
            df = self._resolver_ids(df, EspecialidadeModel, col_busca, 'id_especialidade')

        # --- LIMPEZA FINAL (NaN -> None) ---
        # Converte valores vazios/NaN e strings "nan" (geradas pela conversão de texto) em None
        df = df.replace({np.nan: None, 'nan': None, '': None})
        
        # Garante que None seja passado corretamente para o SQLAlchemy
        df = df.where(pd.notnull(df), None)

        return df.to_dict('records')
    
    def salvar_no_banco(self, dados, Modelo):
        if not dados:
            return

        print(f"--- Inserindo {len(dados)} registros em {Modelo.__tablename__} ---")
        sucessos = 0
        
        for item in dados:
            try:
                novo_objeto = Modelo(**item)
                db.session.add(novo_objeto)
                sucessos += 1
            except Exception as e:
                print(f"   Erro ao preparar item: {e}")

        try:
            db.session.commit()
            print(f"Sucesso! {sucessos} itens processados.\n")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar lote: {e}\n")

    def executar(self, excel_caminho):
        # Ordem obrigatória para resolver dependências
        ordem = ['Especialidades', 'Planos', 'Responsáveis', 'Médicos', 'Cirurgias']
        
        for aba in ordem:
            if aba in self.campos:
                dados = self.processar_planilha(excel_caminho, aba)
                if dados:
                    Modelo = self.mapa_tabelas[aba]
                    self.salvar_no_banco(dados, Modelo)

if __name__ == '__main__':
    with app.app_context():

        db.drop_all()
        db.create_all()

        processador = ProcessadorExcel() 
        processador.executar('template-upload-tags.xlsx')