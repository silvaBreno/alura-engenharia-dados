import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from io import StringIO
from datetime import datetime
import unicodedata

class AgendaTributariaScraper:
    def __init__(self, ano, delay=1):
        self.ano = ano
        self.base_url = f"https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/{ano}"
        self.delay = delay
        self.dados_agenda = {}        
        self.meses = [
            'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
        ]

    def obter_links_meses(self):
        response = requests.get(self.base_url)        
        if response.status_code != 200:
            print(f"Erro ao acessar {self.base_url}: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        links_meses = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith(f"{self.base_url}/") and any(m in a['href'] for m in self.meses)]        
        return links_meses


    def obter_links_datas(self, url_mes):
        response = requests.get(url_mes)        
        if response.status_code != 200:
            print(f"Erro ao acessar {url_mes}: {response.status_code}")
            return []
        soup = BeautifulSoup(response.content, 'html.parser')
        links_datas = [a['href'] for a in soup.select('a') if a.get('href') and a['href'].startswith(response.url) and '/dia-' in a['href']]
        return links_datas

    def extrair_tabelas(self, url_data):        
        response = requests.get(url_data)
        if response.status_code != 200:
            print(f"Erro ao acessar {url_data}: {response.status_code}")
            return []
        soup = BeautifulSoup(response.content, 'html.parser')
        tabelas_html = soup.find_all('table')
        tabelas = []
        for tabela in tabelas_html:
            try:
                df = pd.read_html(StringIO(str(tabela)))[0]
                registros = df.to_dict(orient='records')
                registros_limpos = self.limpar_registros(registros)
                tabelas.append(registros_limpos)
            except Exception as e:
                print(f"Erro ao ler tabela em {url_data}: {e}")
                continue
        return tabelas


    def executar(self):
        print(f'Iniciando o processamento do Web Scrapping da Agenda Tributária do ano de {self.ano}\n')
        links_meses = self.obter_links_meses()
        for link_mes in links_meses:
            nome_mes = link_mes.split('/')[-1]
            print(f"Processando mês: {nome_mes}")            
            self.dados_agenda[nome_mes] = {
                        "url": link_mes,
                        "dias": {}
                    }
            links_datas = self.obter_links_datas(link_mes)
            time.sleep(self.delay)

            for link_data in links_datas:
                nome_data = link_data.split('/')[-1]
                print(f"  - Dia: {nome_data}")                
                eventos = self.extrair_tabelas(link_data)
                self.dados_agenda[nome_mes]["dias"][nome_data] = {
                    "url": link_data,
                    "eventos": eventos
                }
                time.sleep(self.delay)


    def limpar_registros(self, registros):
        registros_limpos = []
        for item in registros:
            # Normaliza as chaves para facilitar acesso
            item_normalizado = {
                self._normalizar_texto(k): v for k, v in item.items()
            }

            tipo = self.classificar_tipo(item_normalizado)

            if tipo in ["darf", "gps", "documento"]:
                periodo = item_normalizado.get("periodo do fato gerador")
            elif tipo in ["declaracao_pf", "declaracao_pj"]:
                periodo = item_normalizado.get("periodo de apuracao")
            else:
                periodo = item_normalizado.get("periodo do fato gerador") or item_normalizado.get("periodo de apuracao")

            # Busca pela descrição
            descricao_html = ""
            for chave in item_normalizado:
                if "descricao" in chave or "declaracoes" in chave:
                    descricao_html = item_normalizado[chave]
                    break

            descricao = BeautifulSoup(descricao_html or "", "html.parser").text.strip()

            registro = {
                "tipo": tipo,
                "codigo_darf": item_normalizado.get("codigo darf"),
                "codigo_gps": item_normalizado.get("codigo gps"),
                "descricao": descricao,
                "periodo_fato_gerador": periodo
            }

            registros_limpos.append(registro)
        return registros_limpos
    
    
    def classificar_tipo(self, item):
        chaves = [self._normalizar_texto(k) for k in item.keys()]

        # Verifica se é DARF
        if any("codigo darf" in k for k in chaves):
            return "darf"

        # Verifica se é GPS
        elif any("codigo gps" in k for k in chaves):
            return "gps"

        # Verifica se é declaração de pessoa jurídica
        elif any(
            "pessoas juridicas" in k and (
                "declaracoes" in k or "documentos" in k or "demonstrativos" in k
            ) for k in chaves
        ):
            return "declaracao_pj"

        # Verifica se é declaração de pessoa física
        elif any(
            "pessoas fisicas" in k and (
                "declaracoes" in k or "documentos" in k or "demonstrativos" in k
            ) for k in chaves
        ):
            return "declaracao_pf"

        # Verifica se é declaração genérica
        elif any("declaracoes" in k or "demonstrativos" in k for k in chaves):
            return "declaracao"

        # Verifica se é documento (fallback)
        elif any("documento" in k for k in chaves):
            return "documento"

        return "outros"


    
    def _normalizar_texto(self, texto):
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        return texto.lower().strip()


    def salvar_json(self, caminho_arquivo=None):
        if not caminho_arquivo:
            caminho_arquivo = f"../data/transformed/teste13_agenda_tributaria_{self.ano}.json"
        
        estrutura_final = {
            "fonte": self.base_url,
            "extraido_em": datetime.today().strftime("%Y-%m-%d"),
            "ano": self.ano,
            "meses": self.dados_agenda
        }

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(estrutura_final, f, ensure_ascii=False, indent=2)
        print(f"Dados salvos com sucesso em '{caminho_arquivo}'.")


# Exemplo de uso
if __name__ == "__main__":
    ano_selecionado = 2025 
    scraper = AgendaTributariaScraper(ano_selecionado)
    scraper.executar()
    scraper.salvar_json()
