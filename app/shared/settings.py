"""Runtime settings from environment variables (docs/security.md: no secrets in code)."""

import os
from dataclasses import dataclass

DEFAULT_DATABASE_URL = "sqlite:///./data/app.db"


@dataclass(frozen=True)
class Settings:
    database_url: str

    @classmethod
    def from_env(cls) -> Settings:
        return cls(database_url=os.environ.get("PLM_DATABASE_URL", DEFAULT_DATABASE_URL))
