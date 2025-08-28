import requests
import pandas as pd
import json
import time
import unicodedata
from io import StringIO
from datetime import datetime
from bs4 import BeautifulSoup
from logger_config import LoggerConfig
from jsonschema import validate, ValidationError

logger = LoggerConfig.configurar_logger()

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
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            links_meses = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith(f"{self.base_url}/") and any(m in a['href'] for m in self.meses)]        
            return links_meses
        except Exception:            
            logger.exception(f"Erro ao acessar ou processar {self.base_url}")
            return []

    def obter_links_datas(self, url_mes):
        try:
            response = requests.get(url_mes)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            links_datas = [a['href'] for a in soup.select('a') if a.get('href') and a['href'].startswith(response.url) and '/dia-' in a['href']]
            return links_datas
        except Exception:                    
            logger.exception(f"Erro ao acessar ou processar {url_mes}")
            return []
    
    def extrair_tabelas(self, url_data): 
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
                    registros_limpos = self.limpar_registros(registros)
                    tabelas.extend(registros_limpos)
                except Exception as e:
                    logger.exception(f"Erro ao ler tabela em {url_data}")                    
            return tabelas
        except Exception:
            logger.exception(f"Erro ao acessar ou processar {url_data}")
            return []

    def executar(self):
        logger.info("=" * 80)
        logger.info(f'Iniciando o processamento do Web Scrapping da Agenda Tributária do ano de {self.ano}')
        logger.info("=" * 80)
        links_meses = self.obter_links_meses()
        for link_mes in links_meses:
            nome_mes = link_mes.split('/')[-1]
            logger.info(f"Processando mês: {nome_mes}")            
            self.dados_agenda[nome_mes] = {
                        "url": link_mes,
                        "dias": {}
                    }
            links_datas = self.obter_links_datas(link_mes)
            time.sleep(self.delay)

            for link_data in links_datas:
                nome_data = link_data.split('/')[-1]
                logger.info(f"  - Dia: {nome_data}")              
                eventos = self.extrair_tabelas(link_data)
                self.dados_agenda[nome_mes]["dias"][nome_data] = {
                    "url": link_data,
                    "eventos": eventos
                }
                time.sleep(self.delay)
        logger.info("-" * 80)
        logger.info(f'Finalizado o processamento da Agenda Tributária do ano de {self.ano}')
        logger.info("-" * 80)


    def limpar_registros(self, registros):
        registros_limpos = []
        for item in registros:
            try:
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
                    "codigo_darf": str(item_normalizado.get("codigo darf")) if item_normalizado.get("codigo darf") is not None else None,
                    "codigo_gps": str(item_normalizado.get("codigo gps")) if item_normalizado.get("codigo gps") is not None else None,
                    "documento": str(item_normalizado.get("documento")) if item_normalizado.get("documento") is not None else None,
                    "descricao": descricao,
                    "periodo_fato_gerador": str(periodo) if periodo is not None else None
                }
                
                registros_limpos.append(registro)
            except Exception:                
                logger.exception("Erro ao limpar registro")
                continue       
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

        # Verifica se é declaração de imóvel rural
        elif any(
            "imovel rural" in k and (
                "declaracoes" in k or "documentos" in k or "demonstrativos" in k
            ) for k in chaves
        ):
            return "declaracao_imovel_rural"

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
        try:
            if not caminho_arquivo:
                caminho_arquivo = f"../data/transformed/teste16_agenda_tributaria_{self.ano}.json"
            
            estrutura_final = {
                "fonte": self.base_url,
                "extraido_em": datetime.today().strftime("%Y-%m-%d"),
                "ano": self.ano,
                "meses": self.dados_agenda
            }

            # Carrega o schema externo
            with open("../schemas/agenda_schema.json", "r", encoding="utf-8") as schema_file:
                agenda_schema = json.load(schema_file)

            # Valida a estrutura dos dados
            validate(instance=estrutura_final, schema=agenda_schema)

            # Salva o JSON
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(estrutura_final, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ JSON validado e salvo com sucesso em '{caminho_arquivo}'.")
        
        except ValidationError as ve:
            logger.exception(f"❌ Erro de validação no JSON: {ve.message}")
        except Exception as e:
            logger.exception(f"❌ Erro ao salvar JSON em {caminho_arquivo}: {e}")


# Exemplo de uso
if __name__ == "__main__":
    ano_selecionado = 2025 
    scraper = AgendaTributariaScraper(ano_selecionado)
    scraper.executar()
    scraper.salvar_json()