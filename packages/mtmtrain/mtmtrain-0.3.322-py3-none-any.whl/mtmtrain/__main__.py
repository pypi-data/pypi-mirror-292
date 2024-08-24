import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from mtmtrain.core.config import settings

sys.path.insert(0, str(Path("mtmlib").resolve()))
from mtmlib.logging import LoggingOptions, setup_logging

load_dotenv()

setup_logging(option=LoggingOptions())
logger = logging.getLogger("mtmtrain")


"""
    在coleb 的使用方式:
    !pip install -U --no-cache-dir "mtmtrain" --index-url https://pypi.org/simple \
    && mtmtrain init
"""


def main():
    print("[🚀 mtmtrain]")

    parser = argparse.ArgumentParser(description="mtmtrain")

    # 添加全局参数
    parser.add_argument(
        "-s",
        "--server-url",
        help="Specify the backend server URL.",
        default="http://localhost:8444",  # 默认 URL
        type=str,
    )

    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")

    # 定义 'init' 子命令
    subparsers.add_parser("init", help="Run initialization.")

    # 定义 'worker' 子命令
    subparsers.add_parser("worker", help="Start the worker process.")

    # 定义 'show1' 子命令
    subparsers.add_parser("show1", help="Show visual output.")

    # 定义 'text_classify' 子命令
    subparsers.add_parser("text_classify", help="Run text classification training.")

    args = parser.parse_args()

    if args.command == "init":
        from mtmtrain import env

        print("Initializing environment...")
        env.init_env()
        print("Environment initialized.")
    elif args.command == "worker":
        from mtmtrain.worker import worker_start

        settings.MTMAI_API_BASE = args.server_url
        worker_start()

    elif args.command == "show1":
        from IPython.display import HTML, display

        def show_visual_output():
            display(HTML("<h1>Processed Data:</h1><pre>88888</pre>"))

        show_visual_output()

    elif args.command == "text_classify":
        from mtmtrain import text_classify

        text_classify.train()
    else:
        print("Unknown command")


if __name__ == "__main__":
    main()
