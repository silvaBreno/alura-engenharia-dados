import os
from dotenv import load_dotenv
import pandas as pd
import mysql.connector 

load_dotenv()

#1 - connect_mysql(host_name, user_name, pw): estabelece a conexão com o servidor MySQL, utilizando os dados do host, usuário e senha. A função deve retornar a conexão estabelecida.
def connect_mysql():
    try:
        cnx = mysql.connector.connect(
            host = os.getenv("DB_HOST"), 
            user = os.getenv("DB_USERNAME"), 
            password = os.getenv("DB_PASSWORD_MYSQL")
        )
        print(f'Objeto de conexao foi criado {cnx}')
        return cnx
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')

#2 - create_cursor(cnx): cria e retorna um cursor, que serve para conseguirmos executar os comandos SQL, utilizando a conexão fornecida como argumento.
def create_cursor(cnx):
    try:
        cursor = cnx.cursor()
        print('Cursor criado com sucesso')
        return cursor
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')

#3 - create_database(cursor, db_name): cria um banco de dados com o nome fornecido como argumento. Para isso, a função deverá usar o cursor para executar o comando SQL de criação do banco de dados.
def create_database(cursor, db_name):
    try:
        sql = f'CREATE DATABASE IF NOT EXISTS {db_name};'
        cursor.execute(operation=sql)
        return db_name
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')
        
#4 - show_databases(cursor): exibe todos os bancos de dados existentes. Para isso, a função deve utilizar o cursor para executar o comando SQL que lista todos os bancos de dados existentes.
def show_databases(cursor):
    try:
        sqlQuery = "SHOW DATABASES;"
        cursor.execute(operation=sqlQuery)
        for db in cursor:
            print(db)
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')

#5 - create_product_table(cursor, db_name, tb_name): cria uma tabela com o nome fornecido no banco de dados especificado. A tabela deve ter as colunas que correspondam aos dados que serão inseridos posteriormente.
def create_product_table(cursor, db_name, tb_name):    
    try:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {db_name}.{tb_name}(
                    id VARCHAR(100),
                    Produto VARCHAR(100),
                    Categoria_Produto VARCHAR(100),
                    Preco FLOAT(10,2),
                    Frete FLOAT(10,2),
                    Data_Compra DATE,
                    Vendedor VARCHAR(100),
                    Local_Compra VARCHAR(100),
                    Avaliacao_Compra INT,
                    Tipo_Pagamento VARCHAR(100),
                    Qntd_Parcelas INT,
                    Latitude FLOAT(10,2),
                    Longitude FLOAT(10,2),
                    
                    PRIMARY KEY (id));
        """)
                    
        print(f"\nTabela {tb_name} criada no banco {db_name} com sucesso!")

        return tb_name
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')

#6 - show_tables(cursor, db_name): lista todas as tabelas existentes no banco de dados especificado. Para isso, a função deve utilizar o cursor para executar o comando SQL que lista todas as tabelas no banco de dados.
def show_tables(cursor, db_name):
    try:
        sql = f"USE {db_name};"
        cursor.execute(operation=sql)
        sql = f"SHOW TABLES;"
        cursor.execute(operation=sql)
        for tb in cursor:
            print(tb)
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')

#7 - read_csv(path): lê um arquivo csv do caminho fornecido e retorna um DataFrame do pandas com esses dados.
def read_csv(path):
    try:
        df = pd.read_csv(path)
        if df.empty:
            print("O DataFrame está vazio, interrompendo a execução.")
            return None
        else:
            print("DataFrame carregado com sucesso.")
            return df
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')

#8 - add_product_data(cnx, cursor, df, db_name, tb_name): insere os dados do DataFrame fornecido à tabela especificada no banco de dados especificado. A função deve usar o cursor para executar o comando SQL de inserção de dados.
def add_product_data(cnx, cursor, df, db_name, tb_name):
    try:
        lista_dados = [tuple(row) for i, row in df.iterrows()]
        sql = f"INSERT INTO {db_name}.{tb_name} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        cursor.executemany(sql, lista_dados)
        cnx.commit()
        print('Os dados foram inseridos com sucesso')
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')


def show_data_table(cursor, db_name, tb_name):
    try:
        sql = f'SELECT * FROM {db_name}.{tb_name} LIMIT 100;'
        cursor.execute(operation=sql)
        print(f'Os dados da tabela {tb_name} abaixo:')
        for row in cursor:
            print(row)
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')

def close_cursor_connection(cursor, connection):
    try:
        cursor.close()
        print(f'O cursor foi fechado com sucesso!')
        connection.close()
        print(f'A conexão foi fechada com sucesso!')
    except Exception as e:
        print(f'Um erro inesperado ocorreu: {e}')

if __name__ == "__main__":
    #conectar ao servidor MySQL;
    conexao = connect_mysql()
    #criar um cursor;
    cursor = create_cursor(conexao)
    #criar um banco de dados chamado "db_produtos_teste";
    database = create_database(cursor=cursor, db_name="db_produtos_teste")
    #exibir todos os bancos de dados existentes;
    show_databases(cursor)
    #criar uma tabela chamada "tb_livros" no banco de dados criado;
    tb_name = create_product_table(cursor, db_name=database,tb_name='tb_livros')
    #exibir todas as tabelas no banco de dados criado;
    show_tables(cursor, database)
    #ler os dados do arquivo csv "tb_livros.csv";
    df = read_csv('./data/tabela_livros.csv')
    #adicionar os dados lidos à tabela criada.
    add_product_data(cnx = conexao, cursor = cursor, df = df, db_name=database, tb_name=tb_name)
    # mostrar os dados para o usuário
    show_data_table(cursor, database, tb_name)
    # fechar cursor e conexao
    close_cursor_connection(cursor, conexao)
