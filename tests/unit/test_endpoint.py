from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_error_not_valid_sort():
    result = client.get("/earth_characters?sort_by=blablabla")
    assert result.status_code == 400

def test_error_not_valid_parameter():
    result = client.get("/earth_characters?not_valid=True")
    assert result.status_code == 400

def test_error_not_found():
    result = client.get("/nowhere")
    assert result.status_code == 404

# Here the get_data function could me mocked to return a fix list of result
# and then test some sorting logic