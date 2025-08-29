from scripts.extractor import AgendaExtractor
from scripts.transformer import AgendaTransformer
from scripts.loader import AgendaLoader
from scripts.logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()
logger.info("🚀 Logger inicializado no main.py")


def run_pipeline(ano):
    logger.info("=" * 80)
    logger.info(f"🚀 Iniciando pipeline de processamento para o ano {ano}")
    logger.info("=" * 80)

    extractor = AgendaExtractor(ano)
    raw_data = extractor.executar()

    transformer = AgendaTransformer(ano, raw_data)
    transformed_data = transformer.transformar()

    loader = AgendaLoader(ano, transformed_data, extractor.base_url)
    loader.salvar_json()

    logger.info("-" * 80)
    logger.info(f"✅ Pipeline finalizado com sucesso para o ano {ano}")
    logger.info("-" * 80)

if __name__ == "__main__":
    run_pipeline(2025)