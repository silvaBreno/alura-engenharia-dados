import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from scripts.logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()

class AgendaExtractor:
    def __init__(self, ano, delay=1):
        self.ano = ano
        self.delay = delay
        self.base_url = f"https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/{ano}"
        self.meses = [
            'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
        ]

    def obter_links_meses(self):
        logger.info(f"🔍 Buscando links dos meses na URL base: {self.base_url}")
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            links_meses = [
                a['href'] for a in soup.find_all('a', href=True)
                if a['href'].startswith(f"{self.base_url}/") and any(m in a['href'] for m in self.meses)
            ]
            logger.info(f"✅ {len(links_meses)} meses encontrados.")
            return links_meses
        except Exception:
            logger.exception(f"❌ Erro ao acessar ou processar {self.base_url}")
            return []

    def obter_links_datas(self, url_mes):
        logger.info(f"🔍 Buscando links de dias no mês: {url_mes}")
        try:
            response = requests.get(url_mes)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            links_datas = [
                a['href'] for a in soup.select('a')
                if a.get('href') and a['href'].startswith(response.url) and '/dia-' in a['href']
            ]
            logger.info(f"✅ {len(links_datas)} dias encontrados em {url_mes}")
            return links_datas
        except Exception:
            logger.exception(f"❌ Erro ao acessar ou processar {url_mes}")
            return []

    def extrair_tabelas(self, url_data):
        logger.info(f"📄 Extraindo tabelas da data: {url_data}")
        try:
            response = requests.get(url_data)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            tabelas_html = soup.find_all('table')
            tabelas = []
            for tabela in tabelas_html:
                try:
                    df = pd.read_html(StringIO(str(tabela)))[0]
                    registros = df.to_dict(orient='records')
                    tabelas.extend(registros)
                except Exception:
                    logger.exception(f"❌ Erro ao ler tabela em {url_data}")
            logger.info(f"✅ {len(tabelas)} registros extraídos de {url_data}")
            return tabelas
        except Exception:
            logger.exception(f"❌ Erro ao acessar ou processar {url_data}")
            return []

    def executar(self):
        logger.info("=" * 80)
        logger.info(f"🚀 Iniciando extração da Agenda Tributária para o ano {self.ano}")
        logger.info("=" * 80)
        dados_agenda = {}
        links_meses = self.obter_links_meses()
        for link_mes in links_meses:
            nome_mes = link_mes.split('/')[-1]
            logger.info(f"📅 Processando mês: {nome_mes}")
            dados_agenda[nome_mes] = {
                "url": link_mes,
                "dias": {}
            }
            links_datas = self.obter_links_datas(link_mes)
            time.sleep(self.delay)

            for link_data in links_datas:
                nome_data = link_data.split('/')[-1]
                logger.info(f"  📆 Dia: {nome_data}")
                eventos = self.extrair_tabelas(link_data)
                dados_agenda[nome_mes]["dias"][nome_data] = {
                    "url": link_data,
                    "eventos": eventos
                }
                time.sleep(self.delay)
        logger.info(f"✅ Extração concluída para o ano {self.ano}")
        return dados_agenda