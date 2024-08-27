from loguru import logger
import logging

class PropogateHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        logging.getLogger(record.name).handle(record)

        
logger.add(PropogateHandler(), format="{message}")