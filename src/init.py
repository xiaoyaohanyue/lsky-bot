import logging
from src.conf.config import *


class yyinit:
    def __init__(self):
        pass

    def setup_logging(self):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(LOG_PATH + '/app.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # 设置全局日志级别为DEBUG
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)    
    
    def check_path(self):
        os.makedirs(SAVE_PATH, exist_ok=True)
        os.makedirs(LOG_PATH, exist_ok=True)
        os.makedirs(SESSION_PATH, exist_ok=True)
        os.makedirs(SQL_PATH, exist_ok=True)
    
    def init(self):
        self.check_path()
        self.setup_logging()
