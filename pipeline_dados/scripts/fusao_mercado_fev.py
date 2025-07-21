from processamento_dados import Dados

path_json = 'data_raw/dados_empresaA.json'
path_csv = 'data_raw/dados_empresaB.csv'

#EXTRACT
print('\n*** EXTRACT ***\n')
dados_empresaA = Dados.leitura_dados(path_json, 'json')
print(f'Empresa A: \n \---> Nº de linhas: {dados_empresaA.qtd_linhas}\n \---> Colunas: {dados_empresaA.nome_colunas}\n')

dados_empresaB = Dados.leitura_dados(path_csv, 'csv')
print(f'Empresa B: \n \---> Nº de linhas: {dados_empresaB.qtd_linhas}\n \---> Colunas: {dados_empresaB.nome_colunas}\n')

#TRANSFORM
print('*** TRANSFORM ***\n')
key_mapping = {'Nome do Item': 'Nome do Produto',
                'Classificação do Produto': 'Categoria do Produto',
                'Valor em Reais (R$)': 'Preço do Produto (R$)',
                'Quantidade em Estoque': 'Quantidade em Estoque',
                'Nome da Loja': 'Filial',
                'Data da Venda': 'Data da Venda'}

dados_empresaB.rename_columns(key_mapping)           
print(f'Novo nome das colunas Empresa B: \n \---> Colunas: {dados_empresaB.nome_colunas}\n')

dados_fusao = Dados.join(dados_empresaA, dados_empresaB)
print(f'Dados Fusão: \n \---> Nº de linhas: {dados_fusao.qtd_linhas}\n \---> Colunas: {dados_fusao.nome_colunas}\n')

#LOAD
print('*** LOAD ***\n')
path_dados_combinados = 'data_processed/dados_combinados.csv'

dados_fusao.salvando_dados(path_dados_combinados)
print(f'Dados Fusão: \n \---> Caminho do Projeto: {path_dados_combinados}\n')