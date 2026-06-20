import sqlite3
import os
from datetime import datetime

# On Render's free tier, the default filesystem is ephemeral — data is lost on redeploy.
# To persist the database across deploys, attach a Render Persistent Disk and set DB_PATH
# to a path on that disk (e.g. /var/data/properties.db).
DB_PATH = os.environ.get("DB_PATH", "properties.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                loan_amount REAL    NOT NULL,
                annual_rate REAL    NOT NULL,
                loan_years  INTEGER NOT NULL,
                fixed_period INTEGER NOT NULL,
                floating_rate REAL  NOT NULL,
                created_at  TEXT    NOT NULL,
                updated_at  TEXT    NOT NULL
            )
        """)


def list_properties():
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM properties ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def get_property(id):
    with _connect() as conn:
        row = conn.execute("SELECT * FROM properties WHERE id = ?", (id,)).fetchone()
    return dict(row) if row else None


def create_property(name, loan_amount, annual_rate, loan_years, fixed_period, floating_rate):
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO properties (name, loan_amount, annual_rate, loan_years, fixed_period, floating_rate, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, loan_amount, annual_rate, loan_years, fixed_period, floating_rate, now, now),
        )
        new_id = cursor.lastrowid
    return get_property(new_id)


def update_property(id, name=None, loan_amount=None, annual_rate=None, loan_years=None, fixed_period=None, floating_rate=None):
    existing = get_property(id)
    if existing is None:
        return None
    fields = {
        "name": name,
        "loan_amount": loan_amount,
        "annual_rate": annual_rate,
        "loan_years": loan_years,
        "fixed_period": fixed_period,
        "floating_rate": floating_rate,
    }
    updated = {k: (v if v is not None else existing[k]) for k, v in fields.items()}
    updated["updated_at"] = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE properties
            SET name=?, loan_amount=?, annual_rate=?, loan_years=?, fixed_period=?, floating_rate=?, updated_at=?
            WHERE id=?
            """,
            (updated["name"], updated["loan_amount"], updated["annual_rate"],
             updated["loan_years"], updated["fixed_period"], updated["floating_rate"],
             updated["updated_at"], id),
        )
    return get_property(id)


def delete_property(id):
    with _connect() as conn:
        conn.execute("DELETE FROM properties WHERE id = ?", (id,))
