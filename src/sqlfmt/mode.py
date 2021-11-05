from dataclasses import dataclass, field
from typing import List

from sqlfmt.dialect import Dialect, Postgres


@dataclass
class Mode:

    SQL_EXTENSIONS: List[str] = field(default_factory=lambda: [".sql", ".sql.jinja"])
    dialect: Dialect = field(default_factory=lambda: Postgres())
    line_length: int = 88
    check: bool = False
    diff: bool = False
    verbose: bool = False
