import os 
from os.path import join
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# intervalo de datas
data_inicio = datetime.today()
data_fim = data_inicio + timedelta(days=7)

# formatando as datas
data_inicio = data_inicio.strftime('%Y-%m-%d')
data_fim = data_fim.strftime('%Y-%m-%d')

city = 'Boston'
access_token = os.getenv('API_TOKEN')

if not access_token:
    raise ValueError("A variável de ambiente API_TOKEN não está definida.")

url = join('https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/',
            f'{city}/{data_inicio}/{data_fim}?unitGroup=metric&include=days&key={access_token}&contentType=csv')

dados = pd.read_csv(url)
print(dados.head())

# criando a pasta para salvar os arquivos
file_path = f'../semana={data_inicio}/'
os.mkdir(file_path)

# salvando os arquivos
dados.to_csv(file_path + 'dados_brutos.csv')
dados[['datetime','tempmin','temp','tempmax']].to_csv(file_path + 'temperaturas.csv')
dados[['datetime','description','icon']].to_csv(file_path + 'condicoes.csv')
f