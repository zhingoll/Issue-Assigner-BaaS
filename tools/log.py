import logging
import os

class Log():
    def __init__(self, model_name, model_name_current_time):
        self.logger = logging.getLogger(model_name)
        self.logger.setLevel(level=logging.DEBUG)

        # Create a directory for logs
        log_dir = './log/'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Set the log file
        log_file = os.path.join(log_dir, model_name_current_time + '.log')
        
        # Remove existing log handlers
        if self.logger.handlers:
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)

        # File logger
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Console logger
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(
        '\033[0;32m%(asctime)s - %(name)s - \033[0;34m%(levelname)s - \033[0m%(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'))

        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, text):
        self.logger.info(text)

    def debug(self, text):
        self.logger.debug(text)
