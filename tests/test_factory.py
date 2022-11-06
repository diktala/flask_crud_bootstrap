from src import create_app


def test_config():
    assert create_app()
