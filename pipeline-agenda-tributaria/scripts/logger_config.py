import logging
import os
from logging.handlers import TimedRotatingFileHandler

class LoggerConfig:
    _logger = None

    @staticmethod
    def configurar_logger(nome_logger="AgendaTributariaLogger", pasta_logs="../logs"):
        if LoggerConfig._logger:
            return LoggerConfig._logger

        # Caminho absoluto para garantir que funcione independente de onde o script é executado
        pasta_logs = os.path.abspath(pasta_logs)
        os.makedirs(pasta_logs, exist_ok=True)

        logger = logging.getLogger(nome_logger)
        logger.setLevel(logging.INFO)
        logger.propagate = False  # Evita propagação para loggers pai

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Adiciona apenas o handler de arquivo com rotação
        if not any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers):
            file_handler = TimedRotatingFileHandler(
                filename=os.path.join(pasta_logs, "agenda_tributaria_scrapper.log"),
                when="midnight",
                interval=1,
                backupCount=30,
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        LoggerConfig._logger = logger
        return logger
