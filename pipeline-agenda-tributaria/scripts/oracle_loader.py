import json
from datetime import datetime
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from .logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()


class OracleLoader:
    """
    Responsável por ler um JSON da agenda e inserir os eventos em uma tabela Oracle.
    """

    def __init__(self, user, password, host, port, service_name, table_name):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.service_name = service_name
        self.table_name = table_name

    def _conn_str(self):
        return f"oracle+oracledb://{self.user}:{self.password}@{self.host}:{self.port}/?service_name={self.service_name}"

    def _parse_date(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None

    def _flatten_json(self, json_path: str | Path):
        path = Path(json_path)
        logger.info(f"📂 Lendo JSON: {path}")
        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        linhas = []
        for mes in data.get("meses", []):
            mes_num = mes.get("mes")
            mes_url = mes.get("url")
            for dia in mes.get("dias", []):
                data_evento = self._parse_date(dia.get("data"))
                dia_url = dia.get("url")
                publicado_em = dia.get("publicado_em")
                atualizado_em = dia.get("atualizado_em")

                dd_ref = data_evento.day if data_evento else None
                mm_ref = data_evento.month if data_evento else None
                aa_ref = data_evento.year if data_evento else None

                for ev in dia.get("eventos", []):
                    linhas.append(
                        {
                            # chaves alinhadas à tabela compromisso
                            "AA_REF_CMPO": aa_ref,
                            "MM_REF_CMPO": mm_ref,
                            "DD_REF_CMPO": dd_ref,
                            "TS_ATL_CMPO": atualizado_em,
                            "CD_RC_CMPO": ev.get("codigo_receita"),
                            "TX_URL_FON_CMPO": mes_url,
                            "TX_GR_TRBT_CMPO": ev.get("grupo_tributo"),
                            "TX_DOC_ARC_CMPO": ev.get("documento_arrecadacao"),
                            "TX_URL_DOC_ARC": dia_url,
                            "TX_DCR_CMPO": ev.get("descricao"),
                            "TX_CTGR_DCL_CMPO": ev.get("categoria_declaracao"),
                            "TX_OGM_LCTO_CMPO": ev.get("origem_escrituracao"),
                            "TX_PER_APRC_CMPO": ev.get("periodo_fato_gerador"),
                            "TX_BASE_LGAL_CMPO": ev.get("fundamentacao_legal"),
                            "TX_URL_BASE_LGAL": ev.get("fundamentacao_legal_url"),
                            "TS_PBC_CMPO": publicado_em,
                        }
                    )

        df = pd.DataFrame(linhas)
        logger.info(f"📊 DataFrame pronto: {df.shape[0]} linhas, {df.shape[1]} colunas")
        return df

    def inserir_json(self, json_path: str | Path, if_exists: str = "append"):
        """
        Lê o JSON da agenda, achata os eventos e insere na tabela Oracle.
        """
        df = self._flatten_json(json_path)
        if df.empty:
            logger.warning("⚠️ Nenhum registro para inserir.")
            return

        conn_str = self._conn_str()
        logger.info(f"🔌 Conectando ao Oracle: {self.host}:{self.port}/{self.service_name}")

        engine = create_engine(conn_str)
        try:
            df.to_sql(self.table_name, con=engine, if_exists=if_exists, index=False)
            logger.info(f"✅ Inserção concluída na tabela '{self.table_name}' ({len(df)} registros).")
        finally:
            engine.dispose()
