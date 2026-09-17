import sqlite3

from sqlalchemy import create_engine  # pyright: ignore[reportMissingImports]
from app.core.config import settings
from app.models.entities import (
    Profile,
    Skill,
    Project,
    Experience,
    Education,
    Certificate,
    Media,
)


SQLITE_DB = "portfolio.db"

sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_conn.row_factory = sqlite3.Row

pg_engine = create_engine(settings.database_url)

tables = [
    (Profile, "profile"),
    (Skill, "skills"),
    (Project, "projects"),
    (Experience, "experience"),
    (Education, "education"),
    (Certificate, "certificates"),
    (Media, "media"),
]

with pg_engine.begin() as pg_conn:

    for model, table_name in tables:
        rows = sqlite_conn.execute(
            f"SELECT * FROM {table_name}"
        ).fetchall()

        if not rows:
            print(f"{table_name}: no data")
            continue

        columns = [column.name for column in model.__table__.columns]

        for row in rows:
            data = {
                column: row[column]
                for column in columns
            }

            # Avoid duplicate primary-key conflicts
            existing = pg_conn.execute(
                model.__table__.select().where(
                    model.__table__.c.id == data["id"]
                )
            ).first()

            if existing:
                print(f"{table_name} id={data['id']}: already exists, skipped")
                continue

            pg_conn.execute(
                model.__table__.insert().values(**data)
            )

        print(f"{table_name}: {len(rows)} row(s) processed")

sqlite_conn.close()

print("\nMigration completed successfully!")