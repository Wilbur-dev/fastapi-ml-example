class ModelRuntime:
    def __init__(self, model, model_path: str):
        self.model = model
        self.model_path = model_path
        self.model_version = "v1"  # 先写死，后面MLflow会替换

    def predict(self, features):
        y = self.model.predict(features)[0]
        prob = self.model.predict_proba(features)[0].tolist()
        return y, prob