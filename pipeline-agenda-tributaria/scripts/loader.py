import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from jsonschema import validate, ValidationError
from .logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()

class AgendaLoader:
    def __init__(self, ano, dados_agenda, base_url, schema_version: str = "1.0"):
        self.ano = ano
        self.dados_agenda = dados_agenda
        self.base_url = base_url
        self.schema_version = schema_version

    def _now_iso_brasilia(self) -> str:
        br_tz = timezone(timedelta(hours=-3))
        return datetime.now(br_tz).isoformat(timespec="seconds")

    # def salvar_json(self, caminho_arquivo=None, caminho_schema=None):
    #     logger.info(f"💾 Salvando JSON da Agenda Tributária para o ano {self.ano}")
    #     try:
    #         if caminho_arquivo is None:
    #             # Constrói o caminho para a pasta data/transformed a partir da raiz do projeto
    #             output_dir = Path(__file__).parent.parent / "data" / "transformed"
    #             output_dir.mkdir(parents=True, exist_ok=True)  # Garante que o diretório exista
    #             caminho_arquivo = output_dir / f"agenda_tributaria_{self.ano}_teste_novembro_dois_layouts_4.json"

    #         estrutura_final = {
    #             "fonte": self.base_url,
    #             "extraido_em": datetime.today().strftime("%Y-%m-%d"),
    #             "ano": self.ano,
    #             "meses": self.dados_agenda
    #         }
    #         if caminho_schema is None:
    #             # Caminho absoluto baseado na raiz do projeto
    #             caminho_schema = Path(__file__).parent.parent / "schemas" / "agenda_schema.json"

    #         with open(caminho_schema, "r", encoding="utf-8") as schema_file:
    #             agenda_schema = json.load(schema_file)

    #         validate(instance=estrutura_final, schema=agenda_schema)

    #         with open(caminho_arquivo, "w", encoding="utf-8") as f:
    #             json.dump(estrutura_final, f, ensure_ascii=False, indent=2)

    #         logger.info(f"✅ JSON validado e salvo com sucesso em '{caminho_arquivo}'.")
    #     except ValidationError as ve:
    #         logger.exception(f"❌ Erro de validação no JSON: {ve.message}")
    #         raise
    #     except Exception as e:
    #         logger.exception(f"❌ Erro ao salvar JSON em {caminho_arquivo}: {e}")
    #         raise

    def salvar_json(self, caminho_arquivo: str | Path = None, caminho_schema: str | Path = None) -> Path:
        """
        Valida e salva o JSON em disco, de forma atômica.
        :returns: Path final do arquivo salvo.
        """
        logger.info(f"💾 Salvando JSON da Agenda Tributária para o ano {self.ano}")

        # 1) Monta estrutura final (contrato canônico)
        
        estrutura_final = {
            "fonte": self.base_url,
            "extraido_em": self._now_iso_brasilia(),
            "ano": self.ano,
            "meses": self.dados_agenda,
            "schema_version": self.schema_version,
        }


        # 2) Caminhos padrão (data/transformed + schemas/agenda_schema.json)
        if caminho_arquivo is None:
            output_dir = Path(__file__).parent.parent / "data" / "transformed"
            output_dir.mkdir(parents=True, exist_ok=True)            
            br_tz = timezone(timedelta(hours=-3))
            timestamp = datetime.now(br_tz).strftime("%Y%m%d_%H%M%S)")
            caminho_arquivo = output_dir / f"agenda_tributaria_{self.ano}_{timestamp}.json"
        else:
            caminho_arquivo = Path(caminho_arquivo)
            caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

        if caminho_schema is None:
            caminho_schema = Path(__file__).parent.parent / "schemas" / "agenda_schema.json"
        else:
            caminho_schema = Path(caminho_schema)

        # 3) Validação pelo JSON Schema
        try:
            with open(caminho_schema, "r", encoding="utf-8") as schema_file:
                agenda_schema = json.load(schema_file)

            validate(instance=estrutura_final, schema=agenda_schema)

            # Métricas rápidas para log
            qtd_meses = len(estrutura_final.get("meses", []))
            qtd_dias = sum(len(m.get("dias", [])) for m in estrutura_final["meses"])
            qtd_eventos = sum(
                sum(len(d.get("eventos", [])) for d in m.get("dias", []))
                for m in estrutura_final["meses"]
            )
            logger.info(
                f"📊 Estrutura validada. Meses={qtd_meses} Dias={qtd_dias} Eventos={qtd_eventos} "
                f"(schema_version={self.schema_version})"
            )

            # 4) Gravação atômica
            tmp_path = caminho_arquivo.with_suffix(".json.tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(estrutura_final, f, ensure_ascii=False, indent=2)
            tmp_path.replace(caminho_arquivo)

            logger.info(f"✅ JSON validado e salvo com sucesso em '{caminho_arquivo}'.")
            return caminho_arquivo

        except ValidationError as ve:
            # mostra caminho do erro dentro do JSON (ex.: ['meses', 0, 'dias', 3, 'eventos', 1, 'tipo'])
            path_str = " > ".join(map(str, ve.path)) if ve.path else "(raiz do documento)"
            logger.exception(f"❌ Erro de validação no JSON (path={path_str}): {ve.message}")
            raise
        except Exception as e:
            logger.exception(f"❌ Erro ao salvar JSON em {caminho_arquivo}: {e}")
            raise
