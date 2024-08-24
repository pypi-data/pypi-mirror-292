# import pytest
# from app import app as flask_app

# @pytest.fixture
# def client():
#     flask_app.config['TESTING'] = True
#     with flask_app.test_client() as client:
#         yield client

# def test_index(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b'Regressors' in response.data

# def test_train_with_insufficient_regressors(client):
#     response = client.post('/train', data={'regressors': ['least_squares']})
#     assert response.status_code == 400
#     assert b'You must select at least two regressors.' in response.data

# def test_train_with_sufficient_regressors(client):
#     response = client.post('/train', data={'regressors': ['least_squares', 'nearest_neighbor']})
#     assert response.status_code == 302  # Should redirect
