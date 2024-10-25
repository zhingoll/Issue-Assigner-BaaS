import logging
import os

class Log():
    def __init__(self, model_name, model_name_current_time):
        self.logger = logging.getLogger(model_name)
        self.logger.setLevel(level=logging.DEBUG)

        # 创建日志目录
        log_dir = './log/'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 设置日志文件
        log_file = os.path.join(log_dir, model_name_current_time + '.log')
        
        # 清除已存在的日志句柄
        if self.logger.handlers:
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)

        # 文件日志
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # 控制台日志
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(
        '\033[0;32m%(asctime)s - %(name)s - \033[0;34m%(levelname)s - \033[0m%(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'))

        # 添加句柄到日志器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, text):
        self.logger.info(text)

    def debug(self, text):
        self.logger.debug(text)
