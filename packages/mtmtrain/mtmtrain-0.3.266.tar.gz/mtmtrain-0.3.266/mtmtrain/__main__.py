import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from mtmtrain.core.config import settings

sys.path.insert(0, str(Path("../mtmlib").absolute()))
from mtmlib.logging import LoggingOptions, setup_logging

load_dotenv()

setup_logging(option=LoggingOptions())
logger = logging.getLogger("mtmtrain")


def main():
    print("[🚀 mtmtrain]")

    parser = argparse.ArgumentParser(description="mtmtrain")

    # 添加全局参数 -s 或 --server-url 来指定后端 URL 地址
    parser.add_argument(
        "-s",
        "--server-url",
        help="Specify the backend server URL.",
        default="http://localhost:8444",  # 默认 URL
        type=str,
    )

    parser.add_argument(
        "command",
        help="Specify the command to run, e.g., 'init' to run initialization.",
        nargs="?",  # 可选位置参数
        default="serve",  # 默认命令为 serve
    )

    args = parser.parse_args()
    if args.command == "worker":
        from mtmtrain.worker import worker_start

        settings.MTMAI_API_BASE = args.server_url

        worker_start()
    else:
        print("unknown command")


if __name__ == "__main__":
    main()
