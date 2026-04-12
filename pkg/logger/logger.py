import logging
import sys
import os
from typing import Any, Dict
import datetime
import json
from logging.handlers import TimedRotatingFileHandler

# 模拟 Go 的日志级别常量
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR

# 颜色代码
COLORS = {
    'DEBUG': '\033[36m',    # 青色
    'INFO': '\033[34m',     # 蓝色
    'WARNING': '\033[33m',  # 黄色
    'ERROR': '\033[31m',    # 红色
    'COLLECT': '\033[35m',  # 紫色（收集日志）
    'RESET': '\033[0m'
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        colored_levelname = f"{COLORS.get(levelname, '')}{levelname}{COLORS['RESET']}"
        record = logging.makeLogRecord(record.__dict__)
        record.levelname = colored_levelname
        return super().format(record)


class Logger:
    def __init__(self):
        self._log = None
        self._collect_loggers: Dict[str, logging.Logger] = {}
        self._project_root = None

    def init_config(self, logPath: str, level: int = logging.INFO):
        """对应 Go 的 InitSystemLogger 逻辑"""
        self._project_root = os.getcwd()
        log_dir = os.path.dirname(logPath)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 系统日志：每天午夜切割，保留7天，格式如 app.log.20260328
        file_handler = TimedRotatingFileHandler(
            logPath,
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        file_handler.suffix = "%Y%m%d"
        file_handler.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter('%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

        logging.basicConfig(
            level=level,
            handlers=[console_handler, file_handler]
        )
        self._log = logging.getLogger("app")

    def _get_caller_path(self):
        f = sys._getframe(2)
        file_path = f.f_code.co_filename
        if self._project_root and file_path.startswith(self._project_root):
            file_path = os.path.relpath(file_path, self._project_root)
        return file_path, f.f_lineno

    # 系统日志方法，支持 %s 格式化
    def Info(self, event: str, *args, **kwargs):
        msg = event % args if args else event
        caller_file, caller_line = self._get_caller_path()
        self._log.info(f"{caller_file}:{caller_line}\t{msg}")

    def Error(self, event: str, *args, **kwargs):
        msg = event % args if args else event
        caller_file, caller_line = self._get_caller_path()
        self._log.error(f"{caller_file}:{caller_line}\t{msg}")

    def Debug(self, event: str, *args, **kwargs):
        msg = event % args if args else event
        caller_file, caller_line = self._get_caller_path()
        self._log.debug(f"{caller_file}:{caller_line}\t{msg}")

    def Exception(self, event: str, *args, **kwargs):
        msg = event % args if args else event
        caller_file, caller_line = self._get_caller_path()
        self._log.exception(f"{caller_file}:{caller_line}\t{msg}")

    def Warning(self, event: str, *args, **kwargs):
        msg = event % args if args else event
        caller_file, caller_line = self._get_caller_path()
        self._log.warning(f"{caller_file}:{caller_line}\t{msg}")

    # 结构化数据收集（类似 Zap 的数据落盘）
    def Collect(self,  message: str, data: Any = None):
        #log_name: str,
        log_name = message+".log"
        """
        高性能收集日志：缓存 Handler，避免频繁打开文件
        """
        f = sys._getframe(1)
        file_path = f.f_code.co_filename
        if self._project_root and file_path.startswith(self._project_root):
            caller_file = os.path.relpath(file_path, self._project_root)
        else:
            caller_file = os.path.basename(file_path)
        caller_line = f.f_lineno

        # 控制台输出（紫色）
        collect_msg = f"{COLORS['COLLECT']}COLLECT{COLORS['RESET']}\t{caller_file}:{caller_line}\t{message}\t{data}"
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t{collect_msg}")

        if log_name not in self._collect_loggers:
            # 自动补全路径
            full_path = f"./logs/{log_name}"
            lgr = logging.getLogger(f"collect_{log_name}")
            lgr.setLevel(logging.INFO)
            lgr.propagate = False  # 不向上传递给 root logger 避免控制台打印

            handler = TimedRotatingFileHandler(
                full_path,
                when='midnight',
                interval=1,
                backupCount=7,
                encoding='utf-8'
            )
            handler.suffix = "%Y%m%d"
            handler.setFormatter(logging.Formatter('%(message)s'))
            lgr.addHandler(handler)
            self._collect_loggers[log_name] = lgr

        record = {
            "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "msg": message,
            "caller": f"{caller_file}:{caller_line}",
            "data": data,
        }

        self._collect_loggers[log_name].info(json.dumps(record, ensure_ascii=False, default=str))


# 单例模式
Log = Logger()


def SetLogger(logger:Logger):
    """
    此函数仅为了保持 API 风格一致
    """
    pass

    #日志默认是./logs/app.log
def InitSystemLogger(logPath: str ="./logs/app.log", level: int =DEBUG):
    Log.init_config(logPath, level)
    return True