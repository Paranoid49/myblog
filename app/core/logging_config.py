"""日志配置模块。

开发环境使用可读格式，生产环境使用 JSON 格式便于日志采集。
"""

import logging
import sys


def setup_logging(environment: str = "development") -> None:
    """根据环境配置日志格式"""
    if environment == "production":
        log_format = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    else:
        log_format = "%(asctime)s %(levelname)-8s %(name)s  %(message)s"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
