import _bootstrap  # noqa: F401

from backend.app.ingestion.seed import seed_demo_data


if __name__ == "__main__":
    print(seed_demo_data())
