
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL

load_dotenv(Path(__file__).resolve().parent / ".env")

url = URL.create(
    "postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.environ["DB_NAME"],
)

engine = create_engine(url)

try:
    inspector = inspect(engine)

    for schema in inspector.get_schema_names():
        if schema in ("information_schema", "pg_catalog"):
            continue

        tables = inspector.get_table_names(schema=schema)
        print(f"\nSchema: {schema}")
        print("Tables:", tables or "(none)")

        if "alembic_version" in tables:
            with engine.connect() as connection:
                from sqlalchemy import text

                revisions = connection.execute(
                    text(
                        f'SELECT version_num FROM "{schema}".alembic_version'
                    )
                ).scalars().all()

                print("Alembic revisions:", revisions)
finally:
    engine.dispose()
