import pytest
import numpy as np
import sys
import os


from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from model import Regressor, EnsembleRegressor, get_user_input



@pytest.fixture
def ensemble():
    regressor_types = ["least_squares", "nearest_neighbor"]
    return EnsembleRegressor(regressor_types)

def test_initialize_regressors(ensemble: any):
     assert len(ensemble.regressors) == len(ensemble.regressor_types)

def test_fit_and_predict():
    X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    y = np.array([3, 5, 7, 9])
    regressor = Regressor(name="least_squares")
    regressor.fit(X, y)
    predictions = regressor.predict(X)
    assert predictions.shape == y.shape
    assert np.allclose(predictions, y, rtol=1e-1)

def test_score_calculation():
    X = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    y = np.array([3, 5, 7, 9])
    regressor = Regressor(name="least_squares")
    regressor.fit(X, y)
    score = regressor.score(X, y)
    expected_score = mean_squared_error(y, regressor.predict(X))
    assert pytest.approx(score) == expected_score

def test_invalid_regressor_type():
    with pytest.raises(ValueError):
        Regressor(name="invalid_type")

def test_get_user_input_invalid(monkeypatch):
    # Mock user input with an invalid selection (less than 2 valid regressors)
    monkeypatch.setattr('builtins.input', lambda: 'least_squares')
    
    # Check if ValueError is raised
    with pytest.raises(ValueError, match="You must select at least two regressors."):
        get_user_input()

def test_get_user_input_some_invalid(monkeypatch):
    # Mock user input with a mix of valid and invalid regressors
    monkeypatch.setattr('builtins.input', lambda: 'least_squares, invalid_regressor, xgboost')
     # Expected output only includes valid regressors
    expected = ['least_squares', 'xgboost']
    
    # Call the function and check the output
    assert get_user_input() == expected

