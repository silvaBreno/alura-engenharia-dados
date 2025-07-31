import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.macros import ds_add
import os 
from os.path import join
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

with DAG(
    dag_id='dados_climaticos',
    start_date=pendulum.datetime(2025, 6, 30, tz='UTC'),
    schedule_interval= '0 0 * * 1', # executar toda segunda feira
) as dag:
    
    # criar pasta
    tarefa_1 = BashOperator(
        task_id = 'cria_pasta',
        bash_command = 'mkdir -p "/home/wsl/AluraProjetos/alura-engenharia-dados/pipeline-apache-airflow/semana={{data_interval_end.strftime("%Y-%m-%d")}}"'
    )

    # extrair os dados da API

    def extrai_dados(data_interval_end):
        
        city = 'Boston'
        access_token = os.getenv('API_TOKEN')

        if not access_token:
            raise ValueError("A variável de ambiente API_TOKEN não está definida.")

        url = join('https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/',
                    f'{city}/{data_interval_end}/{ds_add(data_interval_end, 7)}?unitGroup=metric&include=days&key={access_token}&contentType=csv')

        dados = pd.read_csv(url)

        # criando a pasta para salvar os arquivos
        file_path = f'../semana={data_interval_end}/'

        # salvando os arquivos
        dados.to_csv(file_path + 'dados_brutos.csv')
        dados[['datetime','tempmin','temp','tempmax']].to_csv(file_path + 'temperaturas.csv')
        dados[['datetime','description','icon']].to_csv(file_path + 'condicoes.csv')

    tarefa_2 = PythonOperator(
        task_id = 'extrai_dados',
        python_callable = extrai_dados, 
        op_kwargs = {'data_interval_end': '{{data_interval_end.strftime("%Y-%m-%d")}}'} # dicionario de argumentos de palavras chaves que serao descompactador na funcao que estamos rodando
    )
    # definindo ordem de execução
    tarefa_1 >> tarefa_2