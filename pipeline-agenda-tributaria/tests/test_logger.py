import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

os.makedirs("test_rotacao_logs", exist_ok=True)

logger = logging.getLogger("TesteRotacaoLogger")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = TimedRotatingFileHandler(
        filename="test_logs/teste_rotacao.log",
        when="s",  # rotação por segundo
        interval=5,
        backupCount=5,
        encoding="utf-8"
    )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

for i in range(30):
    logger.info(f"Mensagem de teste número {i+1}")
    time.sleep(1)

print("✅ Teste de rotação de logs concluído. Verifique a pasta 'test_logs'.")
