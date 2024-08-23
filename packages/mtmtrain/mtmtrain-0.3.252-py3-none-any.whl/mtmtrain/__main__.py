import argparse
import logging

from dotenv import load_dotenv
from mtmai.core.config import settings
from mtmai.core.logging import setup_logging

setup_logging()
load_dotenv()
logger = logging.getLogger(__name__)

logger.info(f"main maiai({settings.VERSION}) app starting...")  # noqa: G004


def main():
    print("mtmtrain start ....")
    parser = argparse.ArgumentParser(description="mttrans tool")
    parser.add_argument(
        "command",
        help="Specify the command to run, e.g., 'init' to run initialization.",
        nargs="?",  # 可选位置参数
        default="serve",  # 默认命令为 serve
    )

    args = parser.parse_args()
    if args.command == "bert":
        from mtmai.mtlibs import dev_helper

        dev_helper.init_project()

    elif args.command == "worker":
        from mtmai.worker import worker

        worker.run_worker()


if __name__ == "__main__":
    main()
