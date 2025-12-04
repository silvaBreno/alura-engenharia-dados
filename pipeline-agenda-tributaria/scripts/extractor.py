import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from .logger_config import LoggerConfig
import re

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

            # Regex para capturar datas no formato dia-dd-mm-aaaa OU dd-mm-aaaa e garantir o ano correto
            pattern = re.compile(r'(?:dia-)?(\d{1,2})-(\d{1,2})-(\d{4})')

            links_datas = []
            for a in soup.select('a'):
                href = a.get('href')
                if not href:
                    continue
                match = pattern.search(href)
                if not match:
                    continue
                _, _, year = match.groups()
                if year != str(self.ano):
                    logger.info(f"⚠️ Ignorando link de outro ano: {href}")
                    continue
                links_datas.append(href)

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
            publicado_em, atualizado_em = self._extrair_meta_datas(soup)

            tabelas_html = soup.find_all('table')
            registros = []

            for tabela in tabelas_html:
                cabecalho = [th.get_text(strip=True).lower() for th in tabela.find_all('strong')]
                if "código de receita" in " ".join(cabecalho).lower():
                    logger.info("📐 Layout detectado: NOVO")
                    registros.extend(self._extrair_novo_layout(tabela))
                else:
                    logger.info("📐 Layout detectado: ANTIGO")
                    try:
                        df = pd.read_html(StringIO(str(tabela)))[0]
                        registros.extend(df.to_dict(orient='records'))
                    except Exception:
                        logger.exception(f"❌ Erro ao ler tabela antiga em {url_data}")

            logger.info(f"✅ {len(registros)} registros extraídos de {url_data}")
            return {
                "eventos": registros,
                "publicado_em": publicado_em,
                "atualizado_em": atualizado_em
            }
        except Exception:
            logger.exception(f"❌ Erro ao acessar ou processar {url_data}")
            return {
                "eventos": [],
                "publicado_em": "",
                "atualizado_em": ""
            }

    def _extrair_novo_layout(self, tabela):
        eventos = []
        rows = tabela.select("tbody tr")
        data_rows = rows[2:]  # Ignora cabeçalho
        for i in range(0, len(data_rows), 2):
            linha1 = data_rows[i].find_all("td")
            linha2 = data_rows[i+1].find_all("td")

            evento = {
                "codigo de receita": linha1[0].get_text(strip=True),
                "grupo de tributo": linha1[1].get_text(strip=True),
                "descricao": linha1[2].get_text(strip=True),
                "periodo de apuracao": linha1[3].get_text(" ", strip=True),
                "documento arrecadacao": linha2[0].get_text(strip=True),
                "categoria da declaracao / origem escrituracao": linha2[1].get_text(strip=True),
                "fundamentacao legal": linha2[2].get_text(" ", strip=True)
            }
            eventos.append(evento)
        return eventos


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
                    "publicado_em": eventos.get("publicado_em", ""),
                    "atualizado_em": eventos.get("atualizado_em", ""),
                    "eventos": eventos.get("eventos", [])
                }
                time.sleep(self.delay)
        logger.info(f"✅ Extração concluída para o ano {self.ano}")
        return dados_agenda

    def _extrair_meta_datas(self, soup):
        publicado = ""
        atualizado = ""

        def _coletar(rotulo):
            span_label = soup.find('span', string=lambda s: s and rotulo.lower() in s.lower())
            if span_label:
                valor = span_label.find_next_sibling('span', class_='value')
                if valor:
                    return valor.get_text(strip=True)
            return ""

        publicado = _coletar("Publicado em")
        atualizado = _coletar("Atualizado em")
        return publicado, atualizado

    # def obter_links_datas(self, url_mes):
    #     logger.info(f"🔍 Buscando links de dias no mês: {url_mes}")
    #     try:
    #         response = requests.get(url_mes)
    #         response.raise_for_status()
    #         soup = BeautifulSoup(response.content, 'html.parser')
    #         links_datas = [
    #             a['href'] for a in soup.select('a')
    #             if a.get('href') and a['href'].startswith(response.url) and '/dia-' in a['href']
    #         ]
    #         logger.info(f"✅ {len(links_datas)} dias encontrados em {url_mes}")
    #         return links_datas
    #     except Exception:
    #         logger.exception(f"❌ Erro ao acessar ou processar {url_mes}")
    #         return []

    
