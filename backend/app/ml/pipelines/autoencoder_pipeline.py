from __future__ import annotations

from app.ml.base_model import BaseMaintenanceModel


class AutoencoderMaintenanceModel(BaseMaintenanceModel):
    """Future deep anomaly-detection model placeholder."""

    model_type = "autoencoder"
    version = "not_implemented"

    @classmethod
    def train(cls, training_data, **kwargs):
        raise NotImplementedError("Autoencoder training is not implemented yet.")

    def predict(self, features):
        raise NotImplementedError("Autoencoder prediction is not implemented yet.")

    def save(self, path, scaler_path=None):
        raise NotImplementedError("Autoencoder persistence is not implemented yet.")

    @classmethod
    def load(cls, path, scaler_path=None, metadata=None):
        raise NotImplementedError("Autoencoder loading is not implemented yet.")

    def get_model_info(self):
        return {"model_type": self.model_type, "model_version": self.version}
