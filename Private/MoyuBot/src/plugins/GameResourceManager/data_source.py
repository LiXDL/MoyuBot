import aiosqlite
from pathlib import Path


class DataManager:

    def __init__(self, database: Path):
        self._conn = aiosqlite.connect(database)
