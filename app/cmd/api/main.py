
import sys

sys.path.extend(["./"])

from app import logger
from app.application import app
from app import settings

logger.init_logger(debug=settings.DEBUG)


def main():
    import uvicorn
    uvicorn.run(app,
                host=settings.HOST,
                port=settings.PORT,
                log_level=settings.LOG_LEVEL)


if __name__ == '__main__':
    main()
