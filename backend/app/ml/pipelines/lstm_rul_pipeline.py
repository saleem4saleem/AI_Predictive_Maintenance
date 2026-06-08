from __future__ import annotations

from app.ml.base_model import BaseMaintenanceModel


class LstmRulMaintenanceModel(BaseMaintenanceModel):
    """Future sequence model for Remaining Useful Life estimation."""

    model_type = "lstm_rul"
    version = "not_implemented"

    @classmethod
    def train(cls, training_data, **kwargs):
        raise NotImplementedError("LSTM RUL training is not implemented yet.")

    def predict(self, features):
        raise NotImplementedError("LSTM RUL prediction is not implemented yet.")

    def save(self, path, scaler_path=None):
        raise NotImplementedError("LSTM RUL persistence is not implemented yet.")

    @classmethod
    def load(cls, path, scaler_path=None, metadata=None):
        raise NotImplementedError("LSTM RUL loading is not implemented yet.")

    def get_model_info(self):
        return {"model_type": self.model_type, "model_version": self.version}
