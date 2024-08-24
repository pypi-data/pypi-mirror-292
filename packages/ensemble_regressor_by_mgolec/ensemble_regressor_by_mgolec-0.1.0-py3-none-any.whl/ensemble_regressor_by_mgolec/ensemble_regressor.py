import numpy as np
from .regressor import Regressor

class EnsembleRegressor:
    def __init__(self, regressor_types: list):
        if not regressor_types:
            raise ValueError("The regressor_types list cannot be empty.")
        self.regressors = [Regressor(f"regressor_{i+1}", reg_type) for i, reg_type in enumerate(regressor_types)]

    def fit(self, X, y):
        for regressor in self.regressors:
            regressor.fit(X, y)

    def predict(self, X):
        predictions = [regressor.predict(X) for regressor in self.regressors]
        return np.mean(predictions, axis=0)

    def fit_predict(self, X, y):
        self.fit(X, y)
        return self.predict(X)

    def score(self, X, y):
        predictions = self.predict(X)
        return np.mean([regressor.score(X, y) for regressor in self.regressors])
