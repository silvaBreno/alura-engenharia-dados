import json
from datetime import datetime
from pathlib import Path
from jsonschema import validate, ValidationError
from .logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()

class AgendaLoader:
    def __init__(self, ano, dados_agenda, base_url):
        self.ano = ano
        self.dados_agenda = dados_agenda
        self.base_url = base_url

    def salvar_json(self, caminho_arquivo=None, caminho_schema=None):
        logger.info(f"💾 Salvando JSON da Agenda Tributária para o ano {self.ano}")
        try:
            if caminho_arquivo is None:
                # Constrói o caminho para a pasta data/transformed a partir da raiz do projeto
                output_dir = Path(__file__).parent.parent / "data" / "transformed"
                output_dir.mkdir(parents=True, exist_ok=True)  # Garante que o diretório exista
                caminho_arquivo = output_dir / f"agenda_tributaria_{self.ano}_teste_novembro_dois_layouts_4.json"

            estrutura_final = {
                "fonte": self.base_url,
                "extraido_em": datetime.today().strftime("%Y-%m-%d"),
                "ano": self.ano,
                "meses": self.dados_agenda
            }
            if caminho_schema is None:
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
