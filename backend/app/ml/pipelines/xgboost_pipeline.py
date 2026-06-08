from __future__ import annotations

from app.ml.base_model import BaseMaintenanceModel


class XGBoostMaintenanceModel(BaseMaintenanceModel):
    """Future gradient-boosted failure prediction model placeholder."""

    model_type = "xgboost"
    version = "not_implemented"

    @classmethod
    def train(cls, training_data, **kwargs):
        raise NotImplementedError("XGBoost training is not implemented yet.")

    def predict(self, features):
        raise NotImplementedError("XGBoost prediction is not implemented yet.")

    def save(self, path, scaler_path=None):
        raise NotImplementedError("XGBoost persistence is not implemented yet.")

    @classmethod
    def load(cls, path, scaler_path=None, metadata=None):
        raise NotImplementedError("XGBoost loading is not implemented yet.")

    def get_model_info(self):
        return {"model_type": self.model_type, "model_version": self.version}
