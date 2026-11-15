import os
from pathlib import Path
os.environ["DATABASE_URL"]="sqlite:///"+str(Path(__file__).resolve().parents[1]/"test.db").replace("\\","/")
os.environ.pop("WRITE_TOKEN",None)
import pytest
from backend.app.db import Base, engine, SessionLocal
from backend.app.cli import seed
from backend.app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def db_reset():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    yield

@pytest.fixture
def client():
    with TestClient(app) as c: yield c

@pytest.fixture
def seeded():
    from backend.app.models import SourceSessionRow
    from sqlalchemy import select
    # Seed emits IDs; obtain the same seed result through captured stdout.
    import contextlib, io, json
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture): seed()
    result=json.loads(capture.getvalue())
    return result

@pytest.fixture
def packet():
    return __import__("json").loads(Path(r"C:\Users\rayan\Downloads\simulator (1).json").read_text(encoding="utf-8"))
