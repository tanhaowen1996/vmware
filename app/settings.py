
from pathlib import Path
from typing import Optional

from starlette.config import Config

from app.vmware.types import VC

p: Path = Path(__file__).parents[1] / ".env"
config: Config = Config(p if p.exists() else None)

# srv
DEBUG: int = config("DEBUG", cast=bool, default=False)

HOST: str = config("HOST", cast=str, default="0.0.0.0")
PORT: int = config("PORT", cast=int, default=8000)
LOG_LEVEL: str = "debug" if DEBUG else "info"


# DB
DATABASE: str = config("DATABASE", cast=str, default="cmpvmware")
DB_USER: Optional[str] = config("DB_USER", cast=str, default=None)
# DB_PASSWORD: Optional[Secret] = config("DB_PASSWORD", cast=Secret, default=None)
DB_PASSWORD: str = config("DB_PASSWORD", cast=str, default=None)
DB_HOST: str = config("DB_HOST", cast=str, default="localhost")
DB_PORT: int = config("DB_PORT", cast=int, default=3306)

MYSQL_URL = "mysql+pymysql://{username}:{password}@{host}:{port}/{database}".format(
    username=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DATABASE)


# VC
VC_HOST: str = config("VC_HOST", cast=str, default=None)
VC_PORT: int = config("VC_PORT", cast=int, default=443)
VC_USER: str = config("VC_USER", cast=str, default=None)
# VC_PASSWORD: Optional[Secret] = config("VC_PASSWORD", cast=Secret, default=None)
VC_PASSWORD: str = config("VC_PASSWORD", cast=str, default=None)
VC_INSECURE: bool = config("VC_INSECURE", cast=bool, default=True)
VC_DC: str = config("VC_DC", cast=str, default=None)

VC = VC(host=VC_HOST, port=VC_PORT, user=VC_USER, password=VC_PASSWORD, insecure=VC_INSECURE, dc=VC_DC)


TIME_ZONE = config("TIME_ZONE", cast=str, default='Asia/Shanghai')
