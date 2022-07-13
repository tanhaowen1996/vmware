
from dataclasses import dataclass


@dataclass
class VC:
    host: str
    port: int
    user: str
    password: str
    insecure: bool
    dc: str

