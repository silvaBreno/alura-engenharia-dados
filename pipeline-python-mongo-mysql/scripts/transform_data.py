from extract_and_save_data import verifica_token, connect_mongo, create_connect_db, create_connect_collection
import pandas as pd

## 1 - visualize_collection(col): imprime todos os documentos existentes na coleção.
def visualize_collection(col):
    for docs in col.find():
        print(docs)

## 2 - rename_column(col, col_name, new_name): renomeia uma coluna existente.
def rename_column(col, col_name, new_name):
    try:
        col.update_many({}, {"$rename":{col_name:new_name}})
        print(f'Nome da coluna {col_name} foi alterado para {new_name}')
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')
    

## 3 - select_category(col, category): seleciona documentos que correspondam a uma categoria específica.
def select_category(col, category):
    query = { "Categoria do Produto": f"{category}"}
    lista_categoria = []
    for doc in col.find(query):
        lista_categoria.append(doc)

    return lista_categoria

## 4 - make_regex(col, regex): seleciona documentos que correspondam a uma expressão regular específica.
def make_regex(col, field_name, regex):
    query = {f"{field_name}": {"$regex": fr"{regex}"}}
    list = []
    for docs in col.find(query):
        list.append(docs)
    return list

## 5 - create_dataframe(lista): cria um dataframe a partir de uma lista de documentos.
def create_dataframe(list: list):
    df = pd.DataFrame(list)
    return df

## 6 - format_date(df): formata a coluna de datas do dataframe para o formato "ano-mes-dia".
def format_date(df, column_name):
    print(f'Tipo da coluna antes da transformacao: {df[column_name].dtype.name}')
    df[column_name] = pd.to_datetime(df[column_name], format='%d/%m/%Y', errors='coerce')
    df[column_name] = df[column_name].dt.strftime('%Y-%m-%d')
    return df

## 7 - save_csv(df, path): salva o dataframe como um arquivo CSV no caminho especificado.
def save_csv(df, path):
    df.to_csv(path,index=False)
    print(f'CSV was saved in {path}')

if __name__ == "__main__":
    # estabelecendo a conexão e recuperando os dados do MongoDB
    ## chama o token
    token = verifica_token('DB_PASSWORD')
    ## cria a url de conexao
    uri = f'mongodb+srv://silvaBreno:{token}@cluster-pipeline-estudo.s3yd6yk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-pipeline-estudos'
    ## testa a conexão
    connection_database = connect_mongo(uri)
    ## criando o banco
    db = create_connect_db(connection_database, 'db_vendas')
    ## criando a colecao
    collection = create_connect_collection(db, 'vendas')

    # renomeando as colunas de latitude e longitude
    rename_column(collection, "lat", "Latitude")
    rename_column(collection, "lon", "Longitude")

    # salvando os dados da categoria livros
    livros = select_category(collection, 'livros')
    df = create_dataframe(livros)
    df_formatado = format_date(df, 'Data da Compra')
    save_csv(df_formatado, '../data/livros_script.csv')

    # salvando os dados dos produtos vendidos a partir de 2021
    produtos = make_regex(collection, 'Data da Compra', '/202[1-9]')
    df = create_dataframe(produtos)
    df_formatado = format_date(df, 'Data da Compra')
    save_csv(df_formatado, '../data/produtos_script.csv')
