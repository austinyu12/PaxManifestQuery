import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "manifest.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS flights (
                flight_no   TEXT NOT NULL,
                flight_date TEXT NOT NULL,
                origin      TEXT NOT NULL,
                destination TEXT NOT NULL,
                operator    TEXT,
                PRIMARY KEY (flight_no, flight_date, origin, destination)
            );

            CREATE TABLE IF NOT EXISTS passengers (
                id             INTEGER PRIMARY KEY,
                flight_no      TEXT NOT NULL,
                flight_date    TEXT NOT NULL,
                origin         TEXT NOT NULL,
                destination    TEXT NOT NULL,
                record_locator TEXT,
                last_name      TEXT NOT NULL,
                first_name     TEXT NOT NULL,
                title          TEXT,
                gender         TEXT,
                seat           TEXT,
                cabin_class    TEXT,
                fare_class     TEXT,
                e_ticket_no    TEXT,
                ssr_codes      TEXT,
                notes          TEXT,
                FOREIGN KEY (flight_no, flight_date, origin, destination)
                REFERENCES flights(flight_no, flight_date, origin, destination)
            );

            CREATE TABLE IF NOT EXISTS ssr_codes (
                code        TEXT PRIMARY KEY,
                description TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_passengers_cabin ON passengers(cabin_class);
            CREATE INDEX IF NOT EXISTS idx_passengers_ssr_codes ON passengers(ssr_codes);
        """)
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialised at {DB_PATH}")
