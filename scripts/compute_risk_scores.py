import _bootstrap  # noqa: F401

from backend.app.processing.risk import compute_all_risk_scores


if __name__ == "__main__":
    print(compute_all_risk_scores())
