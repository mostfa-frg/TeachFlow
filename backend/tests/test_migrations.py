import importlib.util
from pathlib import Path

import sqlalchemy as sa
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext


def test_legacy_session_sequence_migration_preserves_and_orders_sessions(monkeypatch):
    migration_path = (
        Path(__file__).parents[1]
        / "migrations"
        / "versions"
        / "0002_legacy_session_sequence.py"
    )
    spec = importlib.util.spec_from_file_location("legacy_session_sequence", migration_path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(
            sa.text(
                "CREATE TABLE teaching_sessions ("
                "id TEXT PRIMARY KEY, topic_id TEXT NOT NULL, created_at TEXT NOT NULL)"
            )
        )
        connection.execute(
            sa.text(
                "INSERT INTO teaching_sessions (id, topic_id, created_at) VALUES "
                "('later', 'topic-a', '2026-01-02'), "
                "('first', 'topic-a', '2026-01-01'), "
                "('other-topic', 'topic-b', '2026-01-01')"
            )
        )
        context = MigrationContext.configure(connection)
        monkeypatch.setattr(migration, "op", Operations(context))

        migration.upgrade()

        actual = connection.execute(
            sa.text(
                "SELECT id, sequence_index FROM teaching_sessions ORDER BY id"
            )
        ).all()
        assert actual == [("first", 1), ("later", 2), ("other-topic", 1)]
        index = next(
            item
            for item in sa.inspect(connection).get_indexes("teaching_sessions")
            if item["name"] == "ix_teaching_sessions_topic_sequence_compat"
        )
        assert index["unique"]

    engine.dispose()
