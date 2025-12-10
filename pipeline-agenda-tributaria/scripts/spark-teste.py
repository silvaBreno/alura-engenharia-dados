from __future__ import annotations

from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, explode
from pyspark.sql.window import Window

from .logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()


class SparkOracleLoader:
    """
    Variante do loader que usa Spark para achatar o JSON e inserir via JDBC no Oracle.
    Útil para volumes maiores e paralelismo.
    """

    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: str,
        service_name: str,
        table_name: str,
        *,
        spark: SparkSession | None = None,
        jar_path: str | None = None,
        batchsize: int = 5000,
        num_partitions: int = 4,
    ):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.service_name = service_name
        self.table_name = table_name
        self.batchsize = batchsize
        self.num_partitions = num_partitions
        self.jar_path = jar_path
        self.spark = spark or self._build_session(jar_path)

    def _build_session(self, jar_path: str | None) -> SparkSession:
        """Cria ou reutiliza uma SparkSession, carregando o driver JDBC se informado."""
        builder = SparkSession.builder.appName("CargaAgendaOracle")
        if jar_path:
            builder = builder.config("spark.driver.extraClassPath", jar_path)
        return builder.getOrCreate()

    def _jdbc_url(self) -> str:
        return f"jdbc:oracle:thin:@//{self.host}:{self.port}/{self.service_name}"

    def _ler_json(self, json_path: str | Path):
        path = Path(json_path)
        logger.info(f"📂 Lendo JSON com Spark: {path}")
        return (
            self.spark.read.option("multiLine", True).json(str(path))
        )

    def _flatten(self, df_raw):
        """
        Achata a estrutura meses/dias/eventos em linhas tabulares para inserção JDBC.
        """
        df = (
            df_raw
            .withColumn("mes", explode("meses"))
            .withColumn("dia", explode("mes.dias"))
            .withColumn("evento", explode("dia.eventos"))
            .select(
                col("evento.nr_idfr_cmpo").cast("long").alias("NR_IDFR_CMPO"),
                col("dia.data").alias("DATA_EVENTO"),
                col("dia.publicado_em").alias("TS_PBC_CMPO"),
                col("dia.atualizado_em").alias("TS_ATL_CMPO"),
                col("evento.codigo_receita").alias("CD_RC_CMPO"),
                col("mes.url").alias("TX_URL_FON_CMPO"),
                col("evento.grupo_tributo").alias("TX_GR_TRBT_CMPO"),
                col("evento.documento_arrecadacao").alias("TX_DOC_ARC_CMPO"),
                col("evento.documento_arrecadacao_url").alias("TX_URL_DOC_ARC"),
                col("evento.descricao").alias("TX_DCR_CMPO"),
                col("evento.categoria_declaracao").alias("TX_CTGR_DCL_CMPO"),
                col("evento.origem_escrituracao").alias("TX_OGM_LCTO_CMPO"),
                col("evento.periodo_fato_gerador").alias("TX_PER_APRC_CMPO"),
                col("evento.fundamentacao_legal").alias("TX_BASE_LGAL_CMPO"),
                col("evento.fundamentacao_legal_url").alias("TX_URL_BASE_LGAL"),
            )
            .withColumn("AA_REF_CMPO", col("DATA_EVENTO").substr(1, 4).cast("int"))
            .withColumn("MM_REF_CMPO", col("DATA_EVENTO").substr(6, 2).cast("int"))
            .withColumn("DD_REF_CMPO", col("DATA_EVENTO").substr(9, 2).cast("int"))
        )
        return df

    def _validar(self, df):
        """
        Verifica obrigatórios e tipos básicos antes da escrita.
        - Colunas numéricas: ID e datas de referência são convertidas para int/long.
        - Obriga não nulos conforme dicionário da tabela (TS_ATL_CMPO é o único opcional).
        """
        required_presence = [
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

        # Verifica presença de colunas
        missing_cols = [c for c in required_presence if c not in df.columns]
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias ausentes: {missing_cols}")

        before_types = {c: t for c, t in df.dtypes if c in required_presence}

        # Força tipos numéricos onde aplicável
        casts = {
            "NR_IDFR_CMPO": "long",
            "AA_REF_CMPO": "int",
            "MM_REF_CMPO": "int",
            "DD_REF_CMPO": "int",
            "CD_RC_CMPO": "int",
        }
        for col_name, tipo in casts.items():
            df = df.withColumn(col_name, col(col_name).cast(tipo))

        # Preenche IDs ausentes com row_number determinístico para primeira carga
        if df.filter(col("NR_IDFR_CMPO").isNull()).limit(1).count() > 0:
            w = Window.orderBy("DATA_EVENTO", "CD_RC_CMPO", "TX_DCR_CMPO")
            df = df.withColumn("NR_IDFR_CMPO", F.coalesce(col("NR_IDFR_CMPO"), F.row_number().over(w)))
            logger.info("🆔 NR_IDFR_CMPO preenchido automaticamente para linhas sem ID.")

        required_not_null = [
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

        nulls = {c: df.filter(col(c).isNull()).limit(1).count() for c in required_not_null}
        faltantes = [c for c, qtd in nulls.items() if qtd > 0]
        if faltantes:
            raise ValueError(f"Colunas obrigatórias com valor nulo ou cast inválido: {faltantes}")

        after_types = {c: t for c, t in df.dtypes if c in required_presence}
        logger.info(f"📐 Tipos antes do cast: {before_types}")
        logger.info(f"📐 Tipos após o cast: {after_types}")

        return df

    def inserir_json(self, json_path: str | Path, mode: str = "append"):
        """
        Lê um JSON transformado, achata com Spark e grava na tabela Oracle via JDBC.
        Usa repartição e batchsize para controle de paralelismo e tamanho dos lotes.
        """
        df_raw = self._ler_json(json_path)
        if df_raw.rdd.isEmpty():
            logger.warning("⚠️ Nenhum registro no JSON.")
            return

        df = self._flatten(df_raw)
        df = self._validar(df)
        total = df.count()

        props = {
            "user": self.user,
            "password": self.password,
            "driver": "oracle.jdbc.driver.OracleDriver",
            "batchsize": str(self.batchsize),
        }

        logger.info(f"🔌 Abrindo sessão JDBC com Oracle em {self.host}:{self.port}/{self.service_name}")
        try:
            (
                df.repartition(self.num_partitions)
                .write
                .mode(mode)
                .jdbc(url=os.getenv('ORACLE_URL'), table=self.table_name, properties=props)
            )
            logger.info(f"✅ Inserção concluída na tabela '{self.table_name}' ({total} registros).")
        except Exception as e:
            logger.exception(f"❌ Falha ao escrever via Spark JDBC no Oracle: {e}")
            raise
