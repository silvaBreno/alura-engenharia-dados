import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

class ManipulaRepositorios:

    def __init__(self, username):
        self.username = username
        self.api_base_url = 'https://api.github.com'
        self.access_token = os.getenv('GITHUB_TOKEN')
        self.headers = {'Authorization': 'Bearer ' + self.access_token,
                        'X-GitHub-Api-Version': '2022-11-28'}

    def cria_repo(self, nome_repo):
        
        data={
            'name': nome_repo,
            'description': 'Dados dos repositórios de algumas empresas',
            'private':False
        }
        response = requests.post(f'{self.api_base_url}/user/repos', json=data,headers= self.headers)
        print(f'Status code de criação do repositório: {response.status_code}')

    def add_arquivo(self, nome_repo, nome_arquivo, caminho_arquivo):
        
        with open(caminho_arquivo, 'rb') as file:
            file_content = file.read()

        encoded_content = base64.b64encode(file_content)

        url = f'{self.api_base_url}/repos/{self.username}/{nome_repo}/contents/{nome_arquivo}'
        data = {
            'message': 'Adicionando um novo arquivo',
            'content': encoded_content.decode('utf-8')
        }

        response = requests.put(url, json=data, headers=self.headers)
        print(f'Status code de upload do arquivo: {response.status_code}')

# Instanciando um objeto
novo_repo = ManipulaRepositorios('silvaBreno')

# Criando um repositório
nome_repo = 'linguagens-mais-utilizadas'
# novo_repo.cria_repo(nome_repo)

# adicionando arquivos salvos no repositorio criado
novo_repo.add_arquivo(nome_repo, 'linguagens_amzn5.csv','dados/linguagens_amzn.csv')
novo_repo.add_arquivo(nome_repo, 'linguagens_netflix5.csv','dados/linguagens_netflix.csv')
novo_repo.add_arquivo(nome_repo, 'linguagens_spotify5.csv','dados/linguagens_spotify.csv')






     