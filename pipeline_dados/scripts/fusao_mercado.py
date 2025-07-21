import json
import csv

def leitura_json(path_json):
    dadas_json = []
    with open(path_json, 'r') as file:
        dados_json = json.load(file)
    return dados_json

def leitura_csv(path_csv):
    dados_csv = []
    with open(path_csv, 'r') as file:
        spamreader = csv.DictReader(file, delimiter=',')
        for row in spamreader:
            dados_csv.append(row)
    return dados_csv

def leitura_dados(path, tipo_arquivo):
    dados = []
    if tipo_arquivo == 'json':
        dados = leitura_json(path)
    elif tipo_arquivo == 'csv':
        dados = leitura_csv(path)
    return dados

def get_columns(dados):
    return list(dados[0].keys())

def rename_columns(dados, key_mapping):
    new_dados_csv = []

    for old_dict in dados:
        dict_temp = {}
        for old_key, value in old_dict.items():
            dict_temp[key_mapping[old_key]] = value        
        new_dados_csv.append(dict_temp)

    return new_dados_csv

def size_data(dados):
    return len(dados)

def join_data(dadosA, dadosB):
    combined_list = []
    combined_list.extend(dadosA)
    combined_list.extend(dadosB)
    return combined_list
    

path_json = 'data_raw/dados_empresaA.json'
path_csv = 'data_raw/dados_empresaB.csv'

# Iniciando a leitura dos dados
dados_json = leitura_dados(path_json, 'json')
nome_colunas_json = get_columns(dados_json)
print(f'Nome colunas dados json: {nome_colunas_json}')

dados_csv = leitura_dados(path_csv, 'csv')
nome_colunas_csv = get_columns(dados_csv)
print(f'Nome colunas dados csv: {nome_colunas_csv}')

print(f'Dados do CSV:  {size_data(dados_csv)} \nDados do JSON: {size_data(dados_json)}\n-------------------\nSomatório:     {size_data(dados_csv) + size_data(dados_json)}')

# Transformando os dados para o formato desejado
key_mapping = {
    'Nome do Item': 'Nome do Produto',
    'Classificação do Produto':'Categoria do Produto',
    'Valor em Reais (R$)':'Preço do Produto (R$)',
    'Quantidade em Estoque':'Quantidade em Estoque',
    'Nome da Loja':'Filial',
    'Data da Venda':'Data da Venda'
}

dados_csv = rename_columns(dados_csv, key_mapping)
nome_colunas_csv = get_columns(dados_csv)
print(f'Novo nome colunas dados csv: {nome_colunas_csv}')

dados_fusao = join_data(dados_json, dados_csv)
nomes_colunas_fusao = get_columns(dados_fusao)
tamanho_dados_fusao = size_data(dados_fusao)
print(nomes_colunas_fusao)
print(tamanho_dados_fusao)
