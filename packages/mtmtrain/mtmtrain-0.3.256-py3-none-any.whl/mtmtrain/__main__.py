import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path("../mtmlib").absolute()))
from mtmlib.logging import LoggingOptions, setup_logging

load_dotenv()

setup_logging(option=LoggingOptions())
logger = logging.getLogger("mtmtrain")


def main():
    print("[🚀 mtmtrain]")
    parser = argparse.ArgumentParser(description="mtmtrain")
    parser.add_argument(
        "command",
        help="Specify the command to run, e.g., 'init' to run initialization.",
        nargs="?",  # 可选位置参数
        default="serve",  # 默认命令为 serve
    )

    args = parser.parse_args()
    if args.command == "worker":
        from mtmtrain.worker import worker_start

        worker_start()
    else:
        print("unknown command")


if __name__ == "__main__":
    main()
