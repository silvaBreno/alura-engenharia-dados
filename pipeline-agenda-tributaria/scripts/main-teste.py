from __future__ import annotations

import os
from dotenv import load_dotenv
from .extractor import AgendaExtractor
from .transformer import AgendaTransformer
from .loader import AgendaLoader
from .oracle_loader import OracleLoader
from .logger_config import LoggerConfig

load_dotenv()

logger = LoggerConfig.configurar_logger()
logger.info("🚀 Logger inicializado no main.py")


def run_pipeline(
    ano: int,
    meses=None,
    carregar_oracle: bool = False,
    usar_spark: bool = False,
    oracle_cfg: dict | None = None,
    datas_ignorar=None,
):
    """
    Executa o pipeline end-to-end e, opcionalmente, carrega no Oracle.
    - carregar_oracle: ativa carga no banco.
    - usar_spark: True para usar loader Spark, False para loader pandas.
    - oracle_cfg: dict com credenciais e opções (user, password, host, port, service_name, table_name, jar_path/batchsize para Spark, chunk_size para pandas).
    """
    logger.info("=" * 80)
    logger.info(f"🚀 Iniciando pipeline de processamento para o ano {ano}")
    logger.info("=" * 80)

    # 1) Extração
    extractor = AgendaExtractor(ano, meses_filtrar=meses, datas_ignorar=datas_ignorar)
    raw_data = extractor.executar()

    # 2) Transformação
    transformer = AgendaTransformer(ano, raw_data)
    transformed_data = transformer.transformar()

    # 3) Salvar JSON transformado
    loader = AgendaLoader(ano, transformed_data, extractor.base_url)
    caminho_json = loader.salvar_json()
    logger.info("-" * 80)
    logger.info(f"✅ JSON transformado salvo em: {caminho_json}")
    logger.info("-" * 80)

    # 4) Carga no Oracle (opcional)
    if carregar_oracle:
        cfg = oracle_cfg or {}
        if usar_spark:
            try:
                from .spark_oracle_loader import SparkOracleLoader
            except ModuleNotFoundError as e:
                raise RuntimeError("pyspark não está instalado. Instale ou defina usar_spark=False.") from e

            loader_db = SparkOracleLoader(
                user=cfg.get("user"),
                password=cfg.get("password"),
               # host=cfg.get("host"),
               # port=cfg.get("port", "1521"),
               # service_name=cfg.get("service_name"),
                table_name=cfg.get("table_name"),
                jar_path=cfg.get("jar_path"),
                batchsize=cfg.get("batchsize", 5000),
                num_partitions=cfg.get("num_partitions", 4),
            )
        else:
            loader_db = OracleLoader(
                user=cfg.get("user"),
                password=cfg.get("password"),
                host=cfg.get("host"),
                port=cfg.get("port", "1521"),
                service_name=cfg.get("service_name"),
                table_name=cfg.get("table_name"),
                chunk_size=cfg.get("chunk_size", 5000),
            )
        loader_db.inserir_json(caminho_json)

    logger.info("-" * 80)
    logger.info(f"✅ Pipeline finalizado com sucesso para o ano {ano}")
    logger.info("-" * 80)


if __name__ == "__main__":

    # Configuração explícita para leitura
    ano_execucao = 2025

    meses_execucao = ["novembro", "dezembro"]
    # ex.: ["novembro", "dezembro"] para restringir; None para todos
    datas_ignorar = ["31-12"]    
    # ex.: ["31-12"] para pular datas específicas ou [] para nenhuma

    # Flags definidas explicitamente (ajuste conforme necessidade)
    carregar_oracle = True  # True para carregar no Oracle, False para pular carga e gerar só JSON
    usar_spark = True        # True usa Spark; False usa pandas.to_sql (só importa se carregar_oracle=True)

    # Credenciais e opções sensíveis (usadas somente se carregar_oracle=True)
    oracle_cfg = None
    if carregar_oracle:
        oracle_cfg = {
            "user": os.getenv("ORACLE_USER"),
            "password": os.getenv("ORACLE_PASSWORD"),
            "host": os.getenv("ORACLE_HOST"),
            "port": os.getenv("ORACLE_PORT", "1521"),
            "service_name": os.getenv("ORACLE_SERVICE_NAME"),
            "table_name": os.getenv("ORACLE_TABLE"),
            # Spark-only:
            "jar_path": os.getenv("ORACLE_JAR_PATH"),
            "batchsize": int(os.getenv("ORACLE_BATCHSIZE", "5000")),
            "num_partitions": int(os.getenv("ORACLE_NUM_PARTITIONS", "4")),
            # Pandas-only:
            "chunk_size": int(os.getenv("ORACLE_CHUNK_SIZE", "5000")),
        }

    run_pipeline(
        ano=ano_execucao,
        meses=meses_execucao,
        carregar_oracle=carregar_oracle,
        usar_spark=usar_spark,
        oracle_cfg=oracle_cfg,
        datas_ignorar=datas_ignorar,
    )
