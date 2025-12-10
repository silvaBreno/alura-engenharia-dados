import logging
import time
from logging.handlers import TimedRotatingFileHandler


# Testa se o handler faz rotação e gera arquivos no diretório temporário
def test_rotacao_logs(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    logger = logging.getLogger("TesteRotacaoLogger")
    logger.setLevel(logging.INFO)

    # Remove handlers antigos para não acumular entre execuções
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    handler = TimedRotatingFileHandler(
        filename=log_dir / "teste_rotacao.log",
        when="s",
        interval=1,
        backupCount=2,
        encoding="utf-8",
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("primeiro")
    time.sleep(1.2)  # força a janela de rotação
    logger.info("segundo")
    logger.info("terceiro")

    for h in logger.handlers:
        h.flush()
        h.close()

    arquivos = list(log_dir.glob("teste_rotacao.log*"))
    assert arquivos, "Nenhum arquivo de log gerado"
