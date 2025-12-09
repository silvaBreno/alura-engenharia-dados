from .extractor import AgendaExtractor
from .transformer import AgendaTransformer
from .loader import AgendaLoader
from .logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()
logger.info("🚀 Logger inicializado no main.py")


def run_pipeline(ano, meses=None):
    logger.info("=" * 80)
    logger.info(f"🚀 Iniciando pipeline de processamento para o ano {ano}")
    logger.info("=" * 80)

    extractor = AgendaExtractor(ano, meses_filtrar=meses)
    raw_data = extractor.executar()

    transformer = AgendaTransformer(ano, raw_data)
    transformed_data = transformer.transformar()

    loader = AgendaLoader(ano, transformed_data, extractor.base_url)
    loader.salvar_json()

    logger.info("-" * 80)
    logger.info(f"✅ Pipeline finalizado com sucesso para o ano {ano}")
    logger.info("-" * 80)

if __name__ == "__main__":
    # Defina aqui o ano e meses que deseja executar. Se meses=None, roda todos.
    ano_execucao = 2025
    #meses_execucao = None  # ex.: ["novembro", "dezembro"] para restringir
    meses_execucao = ["novembro", "dezembro"]  
    run_pipeline(ano_execucao, meses_execucao)
