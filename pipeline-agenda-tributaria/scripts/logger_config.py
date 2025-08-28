import logging
import os
from logging.handlers import TimedRotatingFileHandler

class LoggerConfig:
    @staticmethod
    def configurar_logger(nome_logger="AgendaTributariaLogger", pasta_logs="../logs"):
        os.makedirs(pasta_logs, exist_ok=True)
        logger = logging.getLogger(nome_logger)
        logger.setLevel(logging.INFO)

        if not logger.hasHandlers():
            handler = TimedRotatingFileHandler(
                filename=os.path.join(pasta_logs, "agenda_tributaria_scrapper.log"),
                when="midnight",
                interval=1,
                backupCount=30,
                encoding="utf-8"
            )
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
