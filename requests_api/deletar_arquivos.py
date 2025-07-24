import requests
import base64
import os
from dotenv import load_dotenv
from manipula_repos import ManipulaRepositorios

load_dotenv()

# Instanciando um objeto
novo_repo = ManipulaRepositorios('silvaBreno')

# Criando uma variável para o repositório que ele vai deletar o arquivo
nome_repo = 'linguagens-mais-utilizadas'

# Listas de arquivos que quero deletar
arquivos_para_deletar = ['linguagens_amzn.csv', 'linguagens_apple.csv','linguagens_netflix.csv', 'linguagens_spotify.csv']

for arquivos in arquivos_para_deletar:    
    novo_repo.deletar_arquivo('linguagens-mais-utilizadas', arquivos)
    
    