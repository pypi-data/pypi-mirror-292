import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from xinhou_openai_framework.core.logger.Logger import Logger


class LoggingManager:
    @staticmethod
    def init_logger(app, log_path: str = None):
        """
        初始化日志记录器，将日志同时输出到控制台和指定的文件中。

        :param app: FastAPI 应用程序实例。
        :param log_path: 日志文件路径。如果为 None，则只将日志输出到控制台，不写入文件。
        """
        logger = logging.getLogger()
        # 设置根记录器的日志级别
        logger.setLevel(logging.INFO)
        logger.propagate = False

        # 设置文件处理程序
        if log_path is not None:
            # 根据当前日期生成日志文件名
            file_info = os.path.join(log_path, f"{datetime.now().strftime('%Y-%m-%d')}.log")
            os.makedirs(log_path, exist_ok=True)
            # 创建 RotatingFileHandler 对象
            file_handler = RotatingFileHandler(file_info, maxBytes=1000 * 1024 * 10, backupCount=10)
            file_handler.setLevel(logging.INFO)
            # 设置日志格式
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-4s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
            )
            file_handler.setFormatter(formatter)

        # 设置其他模块的日志处理程序
        # 排除特定的模块，例如 uvicorn、sqlalchemy.pool.impl.QueuePool、apscheduler.executors.default
        excluded = ["uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.pool.impl.QueuePool",
                    "apscheduler.executors.default"]
        for logger_vo in logging.getLogger().manager.loggerDict.items():
            if isinstance(logger_vo[1], logging.Logger):
                if logger_vo[0] not in excluded:
                    sub_logger = logging.getLogger(logger_vo[0])
                    # 移除现有的处理程序
                    for handler in sub_logger.handlers[:]:
                        sub_logger.removeHandler(handler)
                    # 创建流处理器(StreamHandler)，将日志信息输出到控制台
                    console_handler = logging.StreamHandler()
                    console_handler.setFormatter(Logger.colored_formatter())
                    sub_logger.addHandler(console_handler)
                    sub_logger.addHandler(file_handler)
                    sub_logger.propagate = False

    @staticmethod
    def init_before_logger(log_path: str = None):
        logger = logging.getLogger()
        logger.removeHandler(logging.getLogger().handlers[0])

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(Logger.colored_formatter())

        # 设置文件处理程序
        if log_path is not None:
            # 根据当前日期生成日志文件名
            file_info = os.path.join(log_path, f"{datetime.now().strftime('%Y-%m-%d')}.log")
            os.makedirs(log_path, exist_ok=True)
            # 创建 RotatingFileHandler 对象
            file_handler = RotatingFileHandler(file_info, maxBytes=1000 * 1024 * 10, backupCount=10)
            file_handler.setLevel(logging.INFO)
            # 设置日志格式
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-4s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
            )
            file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        skywalking = logging.getLogger('skywalking')
        if len(skywalking.handlers) > 0:
            skywalking.removeHandler(skywalking.handlers[0])
        skywalking.addHandler(file_handler)
        skywalking.addHandler(console_handler)
        skywalking.setLevel(logging.ERROR)
        skywalking.propagate = False

        QueuePool = logging.getLogger('sqlalchemy.pool.impl.QueuePool')
        if len(QueuePool.handlers) > 0:
            QueuePool.removeHandler(QueuePool.handlers[0])
        QueuePool.addHandler(file_handler)
        QueuePool.addHandler(console_handler)
        QueuePool.setLevel(logging.ERROR)
        QueuePool.propagate = False
