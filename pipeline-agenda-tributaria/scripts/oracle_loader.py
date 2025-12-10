"""
Loader baseado em pandas: lê o JSON transformado, achata e insere em Oracle via to_sql.
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()


class OracleLoader:
    """
    Lê um JSON da agenda já transformada, achata os eventos e insere em uma tabela Oracle.
    """

    def __init__(self, user, password, host, port, service_name, table_name, chunk_size: int = 5_000):
        """Guarda credenciais, tabela alvo e tamanho dos lotes (chunk) para inserção."""
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.service_name = service_name
        self.table_name = table_name
        self.chunk_size = chunk_size

    def _conn_str(self) -> str:
        """Monta a string de conexão SQLAlchemy para o Oracle (driver oracledb)."""
        return f"oracle+oracledb://{self.user}:{self.password}@{self.host}:{self.port}/?service_name={self.service_name}"

    def _parse_date(self, value):
        """Converte data ISO (YYYY-MM-DD) em date; retorna None se vier vazio/inválido."""
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None

    def _flatten_json(self, json_path: str | Path) -> pd.DataFrame:
        """
        Achata o JSON hierárquico (meses/dias/eventos) em linhas planas.
        Útil para inserir via pandas.to_sql, que espera tabela tabular.
        """
        path = Path(json_path)
        logger.info(f"📂 Lendo JSON: {path}")
        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        linhas = []
        for mes in data.get("meses", []):
            mes_url = mes.get("url")
            for dia in mes.get("dias", []):
                data_evento = self._parse_date(dia.get("data"))
                publicado_em = dia.get("publicado_em")
                atualizado_em = dia.get("atualizado_em")

                dd_ref = data_evento.day if data_evento else None
                mm_ref = data_evento.month if data_evento else None
                aa_ref = data_evento.year if data_evento else None

                for ev in dia.get("eventos", []):
                    doc_url = ev.get("documento_arrecadacao_url") or ""
                    linhas.append(
                        {
                            # chaves alinhadas à tabela compromisso
                            "NR_IDFR_CMPO": ev.get("nr_idfr_cmpo"),
                            "AA_REF_CMPO": aa_ref,
                            "MM_REF_CMPO": mm_ref,
                            "DD_REF_CMPO": dd_ref,
                            "TS_ATL_CMPO": atualizado_em,
                            "CD_RC_CMPO": ev.get("codigo_receita"),
                            "TX_URL_FON_CMPO": mes_url,
                            "TX_GR_TRBT_CMPO": ev.get("grupo_tributo"),
                            "TX_DOC_ARC_CMPO": ev.get("documento_arrecadacao"),
                            "TX_URL_DOC_ARC": doc_url,
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

    def _validar(self, df: pd.DataFrame):
        """
        Confere colunas obrigatórias, tipos numéricos e nulos conforme a tabela alvo.
        TS_ATL_CMPO permanece opcional; demais obrigatórios não podem ser nulos.
        """
        requeridas_presenca = [
            "NR_IDFR_CMPO",
            "AA_REF_CMPO",
            "MM_REF_CMPO",
            "DD_REF_CMPO",
            "TS_ATL_CMPO",
            "CD_RC_CMPO",
            "TX_URL_FON_CMPO",
            "TX_GR_TRBT_CMPO",
            "TX_DOC_ARC_CMPO",
            "TX_URL_DOC_ARC",
            "TX_DCR_CMPO",
            "TX_CTGR_DCL_CMPO",
            "TX_OGM_LCTO_CMPO",
            "TX_PER_APRC_CMPO",
            "TX_BASE_LGAL_CMPO",
            "TX_URL_BASE_LGAL",
            "TS_PBC_CMPO",
        ]
        faltantes = [c for c in requeridas_presenca if c not in df.columns]
        if faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes: {faltantes}")

        before_types = df[requeridas_presenca].dtypes.to_dict()

        numeric_cols = ["NR_IDFR_CMPO", "AA_REF_CMPO", "MM_REF_CMPO", "DD_REF_CMPO", "CD_RC_CMPO"]
        for col_name in numeric_cols:
            df[col_name] = pd.to_numeric(df[col_name], errors="coerce")

        # Preenche IDs ausentes com sequência simples para primeira carga
        if df["NR_IDFR_CMPO"].isna().any():
            start = int(df["NR_IDFR_CMPO"].max()) if pd.notna(df["NR_IDFR_CMPO"].max()) else 0
            faltantes = df["NR_IDFR_CMPO"].isna().sum()
            df.loc[df["NR_IDFR_CMPO"].isna(), "NR_IDFR_CMPO"] = range(start + 1, start + 1 + faltantes)
            logger.info("🆔 NR_IDFR_CMPO preenchido automaticamente para linhas sem ID.")

        requeridas_not_null = [
            "NR_IDFR_CMPO",
            "AA_REF_CMPO",
            "MM_REF_CMPO",
            "DD_REF_CMPO",
            "CD_RC_CMPO",
            "TX_URL_FON_CMPO",
            "TX_GR_TRBT_CMPO",
            "TX_DOC_ARC_CMPO",
            "TX_URL_DOC_ARC",
            "TX_DCR_CMPO",
            "TX_CTGR_DCL_CMPO",
            "TX_OGM_LCTO_CMPO",
            "TX_PER_APRC_CMPO",
            "TX_BASE_LGAL_CMPO",
            "TX_URL_BASE_LGAL",
            "TS_PBC_CMPO",
        ]
        nulos = [c for c in requeridas_not_null if df[c].isna().any()]
        if nulos:
            raise ValueError(f"Colunas obrigatórias com nulo ou valor inválido: {nulos}")

        after_types = df[requeridas_presenca].dtypes.to_dict()
        logger.info(f"📐 Tipos antes do cast: {before_types}")
        logger.info(f"📐 Tipos após o cast: {after_types}")

        df["NR_IDFR_CMPO"] = df["NR_IDFR_CMPO"].astype("int64")
        return df

    def _to_sql(self, engine: Engine, df: pd.DataFrame, if_exists: str):
        """
        Envia o DataFrame para a tabela Oracle em lotes (chunk_size) para economizar memória.
        """
        df.to_sql(
            self.table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=self.chunk_size,
            method=None,
        )

    def inserir_json(self, json_path: str | Path, if_exists: str = "append"):
        """
        Lê o JSON da agenda, achata os eventos e insere na tabela Oracle.
        Respeita o chunk_size para inserção em blocos e valida IDs antes de gravar.
        """
        df = self._flatten_json(json_path)
        if df.empty:
            logger.warning("⚠️ Nenhum registro para inserir.")
            return

        df = self._validar(df)

        conn_str = self._conn_str()
        logger.info(f"🔌 Conectando ao Oracle: {self.host}:{self.port}/{self.service_name}")

        engine = create_engine(conn_str)
        try:
            self._to_sql(engine, df, if_exists)
            logger.info(f"✅ Inserção concluída na tabela '{self.table_name}' ({len(df)} registros).")
        except Exception as e:
            logger.exception(f"❌ Falha ao escrever via pandas.to_sql no Oracle: {e}")
            raise
        finally:
            engine.dispose()
