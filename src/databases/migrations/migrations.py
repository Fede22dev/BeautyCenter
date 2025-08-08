import os.path
import shutil
from datetime import datetime

from PySide6.QtCore import qDebug
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from src.core.paths_utils import get_resource_path
from src.databases.local.local_db import engine, SQLALCHEMY_DATABASE_URL
from src.name_version import DB_PATH

_ID_TAG = "[DB_MIGRATION]"

alembic_cfg = Config(get_resource_path("alembic/alembic.ini"))
alembic_cfg.set_main_option("script_location", get_resource_path("src/databases/migrations"))
alembic_cfg.set_main_option("prepend_sys_path", ".")
alembic_cfg.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)


def stamp_alembic_head() -> None:
    command.stamp(alembic_cfg, "head")


def run_auto_migrations() -> None:
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()

    script = ScriptDirectory.from_config(alembic_cfg)
    head_rev = script.get_current_head()

    if current_rev != head_rev:
        qDebug(f"{_ID_TAG} DB Upgrade needed: {current_rev} -> {head_rev}")
        _backup_db()
        command.upgrade(alembic_cfg, "head")
        qDebug(f"{_ID_TAG} DB migration to head applied")
    else:
        qDebug(f"{_ID_TAG} DB is up-to-date")


def _backup_db() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = get_resource_path(f"{DB_PATH}.db")
    backup_dir = get_resource_path(f"{DB_PATH}_db_bak")
    backup_file = os.path.join(backup_dir, f"{DB_PATH}.{timestamp}.bak")

    try:
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copyfile(db_path, backup_file)
        qDebug(f"{_ID_TAG} DB Backup created: {backup_file}")
    except Exception as e:
        qDebug(f"{_ID_TAG} DB Failed to create backup: {e}")
