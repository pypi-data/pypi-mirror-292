from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor

class Regressor:
    def __init__(self, name: str, model_type: str):
        self.name = name
        self.model_type = model_type
        self.model = self._initialize_model(model_type)

    def _initialize_model(self, model_type):
        if model_type == 'least_squares':
            return LinearRegression()
        elif model_type == 'nearest_neighbor':
            return KNeighborsRegressor()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def fit_predict(self, X, y):
        self.fit(X, y)
        return self.predict(X)

    def score(self, X, y):
        return self.model.score(X, y)
