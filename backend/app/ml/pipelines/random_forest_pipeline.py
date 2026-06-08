from __future__ import annotations

from app.ml.base_model import BaseMaintenanceModel


class RandomForestMaintenanceModel(BaseMaintenanceModel):
    """Future supervised failure-classification model.

    Expected future output shape should match the standard prediction
    dictionary returned by active backend models.
    """

    model_type = "random_forest"
    version = "not_implemented"

    @classmethod
    def train(cls, training_data, **kwargs):
        raise NotImplementedError("Random Forest training is not implemented yet.")

    def predict(self, features):
        raise NotImplementedError("Random Forest prediction is not implemented yet.")

    def save(self, path, scaler_path=None):
        raise NotImplementedError("Random Forest persistence is not implemented yet.")

    @classmethod
    def load(cls, path, scaler_path=None, metadata=None):
        raise NotImplementedError("Random Forest loading is not implemented yet.")

    def get_model_info(self):
        return {"model_type": self.model_type, "model_version": self.version}
