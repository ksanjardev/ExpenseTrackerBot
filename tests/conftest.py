import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture()
def fresh_db(tmp_path, monkeypatch):
    import config
    import db
    monkeypatch.setattr(config, "SQLITE_PATH", str(tmp_path / "t.db"))
    monkeypatch.setattr(config, "DATABASE_URL", os.getenv("TEST_DATABASE_URL", ""))   # set it to run on Postgres
    monkeypatch.setattr(db, "_engine", None)
    if config.DATABASE_URL:
        db.metadata.drop_all(db.engine())
    db.init()
    yield db
    if db._engine is not None:
        db._engine.dispose()
