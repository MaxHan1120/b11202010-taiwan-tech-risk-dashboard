import _bootstrap  # noqa: F401

from backend.app.database import init_db


if __name__ == "__main__":
    init_db()
    print("Initialized SQLite database and tracked stock list.")
