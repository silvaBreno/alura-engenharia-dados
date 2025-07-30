import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()
# verificar se a variavel de ambiente foi carregada
def verifica_token(key_name):

    access_token = os.getenv(f'{key_name}')

    if not access_token:
        raise ValueError(f'A variável de ambiente {key_name} não está definida.')

    else:
        print(f'A variável de ambiente {key_name} foi definida com sucesso.')
        return access_token
 
# verificar e criacao da conexao com o mongodb
def connect_mongo(uri):
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(e)
# criar o banco
def create_connect_db(client, db_name):
    try:
        print(f'Your database was created as {db_name} database')
        return client[f'{db_name}']
    except Exception as e:
        print(e)

# criar colecao
def create_connect_collection(db, col_name):
    try:
        print(f'Your collection database was created as {col_name} collection')
        return db[f'{col_name}']
    except Exception as e:
        print(e)

# fazer a conexao com a API 
def extract_api_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print('Your JSON response was successfully returned')
            return response.json()
        else:
            print(f'Error: {response.status_code}')
    except Exception as e:
        print(e)
    
# atribuir o retorno da API e inserir no banco novo
def insert_data(col,data):
    try: 
        print(f'Number of documents in API to be inserted: {len(data)}')
        docs = col.insert_many(data)
        n_docs_inseridos = len(docs.inserted_ids)
        return n_docs_inseridos
    except Exception as e:
        print(e)

if __name__ == "__main__":
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

    print(f'Number of documents before extraction: {collection.count_documents({})}')
    ## extraindo os dados da API
    url = 'https://labdados.com/produtos'
    data = extract_api_data(url)

    ## inserindo os dados da API no banco de dados
    if data:
        print(f'Number of data extracted: {len(data)}')
        result = insert_data(collection, data)
        if result:
            print(f'Number of documents after extraction: {result}')
    else:
        print('Nenhum dado foi retornado pela API.')

    connection_database.close()



