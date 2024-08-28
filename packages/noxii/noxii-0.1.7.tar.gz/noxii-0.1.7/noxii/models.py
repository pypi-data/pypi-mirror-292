from dataclasses import dataclass
from datetime import date


@dataclass
class Database:
    database: str
    collection: str
    find1: str
    find2: str
    value: str