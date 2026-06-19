import _bootstrap  # noqa: F401

from backend.app.ingestion.finmind import update_from_finmind
from backend.app.ingestion.seed import seed_demo_data


if __name__ == "__main__":
    try:
        counts = update_from_finmind()
        print({"source": "finmind", **counts})
    except Exception as exc:
        counts = seed_demo_data()
        print({"source": "demo_fallback", "error": str(exc), **counts})
