from contextlib import contextmanager
from time import time

import logging  # 导入 logging 模块
from datetime import datetime
import sys
from loguru import logger

class TimeInspector:

    timer_logger = logger

    time_marks = []

    @classmethod
    def set_time_mark(cls):
        """
        Set a time mark with current time, and this time mark will push into a stack.
        :return: float
            A timestamp for current time.
        """
        _time = time()
        cls.time_marks.append(_time)
        return _time

    @classmethod
    def pop_time_mark(cls):
        """
        Pop last time mark from stack.
        """
        return cls.time_marks.pop()

    @classmethod
    def get_cost_time(cls):
        """
        Get last time mark from stack, calculate time diff with current time.
        :return: float
            Time diff calculated by last time mark with current time.
        """
        cost_time = time() - cls.time_marks.pop()
        return cost_time

    @classmethod
    def log_cost_time(cls, info="Done"):
        """
        Get last time mark from stack, calculate time diff with current time, and log time diff and info.
        :param info: str
            Info that will be logged into stdout.
        """
        cost_time = time() - cls.time_marks.pop()
        cls.timer_logger.info("Time cost: {0:.3f}s | {1}".format(cost_time, info))

    @classmethod
    @contextmanager
    def logt(cls, name="", show_start=False):
        """logt.
        Log the time of the inside code

        Parameters
        ----------
        name :
            name
        show_start :
            show_start
        """
        if show_start:
            cls.timer_logger.info(f"{name} Begin")
        cls.set_time_mark()
        try:
            yield None
        finally:
            pass
        cls.log_cost_time(info=f"{name} Done")


# 设置日志格式，包含行号和线程号
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(thread)d - %(message)s"
)


# 自定义日志记录器
def setup_logger(name, log_level=logging.DEBUG):
    _logger = logging.getLogger(name)
    _logger.setLevel(log_level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    # 创建文件处理器，按时间生成文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_filename = f"control_{timestamp}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    # 创建专门处理 ERROR 级别的文件处理器
    error_log_filename = f"error_{timestamp}.log"
    error_file_handler = logging.FileHandler(error_log_filename)
    error_file_handler.setLevel(logging.ERROR)  # 只处理 ERROR 及以上级别的日志
    error_file_handler.setFormatter(formatter)
    _logger.addHandler(error_file_handler)

    return _logger


loguru_format = "<green>{time:MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"


def setup_logger_loguru(
    name, file_name="robot_control.log", log_level=logging.DEBUG, enqueue=True
):
    from loguru import logger as _logger  # 新增：导入loguru模块

    # 添加单例保护
    if hasattr(setup_logger_loguru, "_initialized"):
        return _logger
    setup_logger_loguru._initialized = True

    # 配置Loguru异步日志
    _logger.remove()  # 移除默认控制台输出
    _logger.add(
        sys.stdout,
        level=log_level,
        format=loguru_format,
        enqueue=enqueue,  # 启用异步写入
        backtrace=True,
        diagnose=True,
    )

    # 新增：配置异步日志
    # logger.add(
    #     file_name,
    #     enqueue=True,  # 启用异步写入
    #     rotation="500 MB",  # 日志轮转
    #     level=log_level,
    #     format=loguru_format,
    # )

    # 2. 全局日志文件（所有日志）
    _logger.add(
        sink="logs/app.log",
        format=loguru_format,
        level=log_level,
        enqueue=enqueue,
        rotation="100 MB",
        retention="30 days",
    )

    # 3. 机器人控制模块日志（仅 RobotControl）
    _logger.add(
        sink="logs/robot_control.log",
        format=loguru_format,
        level=log_level,
        enqueue=enqueue,
        rotation="50 MB",
        retention="30 days",
        filter=lambda record: record["extra"].get("logger_name") == "RobotControl",
    )

    # 4. sbus.py模块日志（仅 Sbus）
    _logger.add(
        sink="logs/remote_control.log",
        format=loguru_format,
        level=log_level,
        enqueue=enqueue,
        rotation="50 MB",
        retention="30 days",
        filter=lambda record: record["extra"].get("logger_name") == "RemoteControl",
    )

    # 4. 传感器模块日志（仅 Sensor）
    _logger.add(
        sink="logs/debug_only.log",
        format=loguru_format,
        level=log_level,
        enqueue=enqueue,
        rotation="50 MB",
        retention="30 days",
        filter=lambda record: record["extra"].get("logger_name") == "debug_only",
    )

    _logger.bind(logger_name="LoggerUtils").info(
        "日志系统初始化完成，异步模式:{}", enqueue
    )
    return _logger


def test_TimeInspector():
    with TimeInspector.logt("The time with reusing processed data in memory:"):
        # this will save the time to reload and process data from disk(in `DataHandlerLP`)
        # It still takes a lot of time in the backtest phase
        for i in range(20):
            # print('The time with reusing processed data in memory:')
            logger.info("The time with reusing processed data in memory:")


if __name__ == "__main__":
    test_TimeInspector()
