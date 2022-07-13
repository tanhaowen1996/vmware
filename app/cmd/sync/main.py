
import sys

sys.path.extend(["./"])

from app import logger
from app.settings import DEBUG
from app.scheduler.manager import scheduler_start_with_dlock

logger.init_logger(debug=DEBUG)


def main():
    scheduler_start_with_dlock()


if __name__ == '__main__':
    main()
