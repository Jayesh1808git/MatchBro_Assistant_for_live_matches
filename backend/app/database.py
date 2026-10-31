
import sqlite3
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "matchbro.db"
)


def get_connection():

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS match_events (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                match_id TEXT NOT NULL,

                over_number INTEGER NOT NULL,

                ball_number INTEGER NOT NULL,

                elapsed_seconds INTEGER NOT NULL,

                batter TEXT NOT NULL,

                bowler TEXT NOT NULL,

                outcome TEXT NOT NULL,

                runs INTEGER NOT NULL,

                wicket INTEGER NOT NULL,

                commentary TEXT NOT NULL
            )
        """)

        connection.commit()


def save_event(event):

    with get_connection() as connection:

        connection.execute("""
            INSERT INTO match_events (
                match_id,
                over_number,
                ball_number,
                elapsed_seconds,
                batter,
                bowler,
                outcome,
                runs,
                wicket,
                commentary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event["match_id"],
            event["over_number"],
            event["ball_number"],
            event["elapsed_seconds"],
            event["batter"],
            event["bowler"],
            event["outcome"],
            event["runs"],
            event["wicket"],
            event["commentary"]
        ))

        connection.commit()


def get_recent_events(limit=12):

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT *
            FROM match_events
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [
        dict(row)
        for row in reversed(rows)
    ]


def get_all_events():

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT *
            FROM match_events
            ORDER BY id ASC
        """).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def clear_events():

    with get_connection() as connection:

        connection.execute(
            "DELETE FROM match_events"
        )

        connection.commit()
