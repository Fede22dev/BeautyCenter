# pydantic per i modelli/oggetti, sqlite3 per db + sqlalchemy + alembic e
# supabase-py (cioè libreria ufficiale di supabase per python),
# per sync db online con qthread per non bloccare la gui durante le query o update etc.
from PySide6.QtCore import qDebug
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from src.databases.models.models import Base
from src.name_version import DB_PATH

_ID_TAG = "[LOCAL_DB]"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    qDebug(f"{_ID_TAG} DB and tables created.")


def is_db_empty() -> bool:
    inspector = inspect(engine)
    return not inspector.get_table_names()
