import os
import sys
from logging.config import fileConfig

from alembic import context

# Leave it like this, or it not works in cmd when gen a new version
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.databases.local.local_db import engine
from src.databases.models.models import Base

# Access to the values in the .ini file in use
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            compare_type=True,
            render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

# TO OVERWRITE ALL EXISTING MIGRATION FILES WITH NEW MIGRATION FIRST DELETE ALEMBIC_VERSION FROM DB

# COMMAND TO GENERATE MIGRATION FILES FROM ROOT DIRECTORY:
# alembic -c alembic/alembic.ini revision --autogenerate -m "message here"

# COMMAND TO APPLY MIGRATION FILES FROM ROOT DIRECTORY:
# alembic -c alembic/alembic.ini upgrade head

# COMMAND TO DOWNGRADE MIGRATION FILES FROM ROOT DIRECTORY:
# alembic -c alembic/alembic.ini downgrade base

# COMMAND TO ROLLBACK MIGRATION FILES FROM ROOT DIRECTORY:
# alembic -c alembic/alembic.ini rollback head
