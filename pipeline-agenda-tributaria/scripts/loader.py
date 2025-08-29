import json
from datetime import datetime
from pathlib import Path
from jsonschema import validate, ValidationError
from scripts.logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()

class AgendaLoader:
    def __init__(self, ano, dados_agenda, base_url):
        self.ano = ano
        self.dados_agenda = dados_agenda
        self.base_url = base_url

    def salvar_json(self, caminho_arquivo=None, caminho_schema=None):
        logger.info(f"💾 Salvando JSON da Agenda Tributária para o ano {self.ano}")
        try:
            if not caminho_arquivo:
                caminho_arquivo = f"../data/transformed/teste17_agenda_tributaria_{self.ano}.json"

            estrutura_final = {
                "fonte": self.base_url,
                "extraido_em": datetime.today().strftime("%Y-%m-%d"),
                "ano": self.ano,
                "meses": self.dados_agenda
            }
            if not caminho_schema:
                # Caminho absoluto baseado na raiz do projeto
                caminho_schema = Path(__file__).parent.parent / "schemas" / "agenda_schema.json"

            with open(caminho_schema, "r", encoding="utf-8") as schema_file:
                agenda_schema = json.load(schema_file)

            validate(instance=estrutura_final, schema=agenda_schema)

            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(estrutura_final, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ JSON validado e salvo com sucesso em '{caminho_arquivo}'.")
        except ValidationError as ve:
            logger.exception(f"❌ Erro de validação no JSON: {ve.message}")
            raise
        except Exception as e:
            logger.exception(f"❌ Erro ao salvar JSON em {caminho_arquivo}: {e}")
            raise
