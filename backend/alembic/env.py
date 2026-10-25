from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.core.config import settings

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

# shortcut: sin metadata hasta que exista el primer modelo; se conecta al Base del primer módulo
target_metadata = None


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url().render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with create_engine(settings.database_url()).connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
