import pytest
from src import create_app


@pytest.fixture
def app():
    app = create_app()

    with app.app_context():
        print("testing 123")

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
