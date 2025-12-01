import pytest

@pytest.mark.django_db
def test_conexao_api(client):
    home = client.get('/')
    assert home.status_code == 200