from app.ml.train import train_isolation_forest_from_sample_data


def run_retraining_job() -> dict:
    return train_isolation_forest_from_sample_data()
