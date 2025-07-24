import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class DadosRepositorios:

    def __init__(self, owner):
        self.owner = owner
        self.api_base_url = 'https://api.github.com'
        self.access_token = os.getenv('GITHUB_TOKEN')
        self.headers = {'Authorization': 'Bearer ' + self.access_token,
                        'X-GitHub-Api-Version': '2022-11-28'}

    def lista_repositorios(self):
        repos_list = []
        page_num = 1

        while True:
            try:
                url = f'{self.api_base_url}/users/{self.owner}/repos?page={page_num}'
                response = requests.get(url, headers=self.headers)
                data = response.json()

                # Se a resposta estiver vazia, não há mais repositórios
                if not data:
                    break

                repos_list.append(data)  # adiciona os repositórios à lista
                page_num += 1

            except Exception as e:
                print(f"Erro na página {page_num}: {e}")
                break

        return repos_list

    def nomes_repos(self, repos_list):
        repo_names=[]
        for page in repos_list:
            for repo in page:
                try:
                    repo_names.append(repo['name'])
                except:
                    pass
        return repo_names

    def nomes_linguagens(self, repos_list: list): 
        repo_languages = []
        for page in repos_list:
            for repo in page:
                try:
                    repo_languages.append(repo['language'])
                except:
                    pass

        return repo_languages

    def cria_df_linguagens(self):

        repositorios = self.lista_repositorios()
        nomes = self.nomes_repos(repositorios)
        linguagens = self.nomes_linguagens(repositorios)

        dados = pd.DataFrame()
        dados['repository_name'] = nomes
        dados['language'] = linguagens

        # Salvando os dados
        dados.to_csv(f'dados/linguagens_{self.owner}.csv')
        return dados


amazon_rep = DadosRepositorios('amzn')
ling_mais_usadas_amzn = amazon_rep.cria_df_linguagens()

netflix_rep = DadosRepositorios('netflix')
ling_mais_usadas_netflix = netflix_rep.cria_df_linguagens()

spotify_rep = DadosRepositorios('spotify')
ling_mais_usadas_spotify = spotify_rep.cria_df_linguagens()

apple_rep = DadosRepositorios('apple')
ling_mais_usadas_apple = apple_rep.cria_df_linguagens()