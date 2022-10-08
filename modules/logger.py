import os
import logging
from logging.handlers import TimedRotatingFileHandler

class Logs:
    """
    this is singleton class
    this class inherits from File
    """
    _singleton = None

    def __init__(self, path, file_name, logger_name):

        if self.__initialized:
            return
        self.__initialized = True
        self.__logger_name = logger_name
        stream_log_handler = logging.StreamHandler()
        file_handler = TimedRotatingFileHandler(filename=path + file_name, encoding='utf-8', when='h', interval=1,
                                                backupCount=100)
        log_formatter = logging.Formatter(u'%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(message)s')
        stream_log_handler.setFormatter(log_formatter)
        file_handler.setFormatter(log_formatter)
        self.logger = logging.getLogger(logger_name)
        self.logger.addHandler(stream_log_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)

    def __new__(cls, path, name, logger_name):
        if not cls._singleton:
            cls._singleton = super(Logs, cls).__new__(cls)
            cls._singleton.__initialized = False
        return cls._singleton

    @classmethod
    def create_logger(cls, logger_path, logger_filename, logger_name):
        logger = cls(logger_path, logger_filename, logger_name)
        return logger.logger

    def removeLast(self):
        files = os.listdir(self.LOGPATH)
        number_files = len(files)

        if number_files > 9:
            os.remove(self.LOGPATH + files[-1])