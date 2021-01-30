import pytest
from mongoengine import disconnect, connect
from app import app


@pytest.fixture(scope='module')
def client():
    """Generate test client for every module.
    How to use this fixture for a method:
    ```
    def test_xxx(self, client):
        # Use client to make request
    ```
    """
    with app.test_client() as client:
        with app.app_context():
            app.config.update(
                TESTING=True,
                ENV='test'
            )
        yield client


@pytest.fixture(scope="function")
def mongo(request):
    """Use this fixtures for setup and teardown database every test method.
    How to use this fixture for a method:
    ```
    def test_xxx(self, mongo):
    ```
    How to use this fixture for every method on a class:
    ```
    import pytest
    from utils.fixtures import mongo
    @pytest.mark.usefixtures('mongo')
    class SiteTests:
    ```
    """
    # Set up
    disconnect()
    db = connect("testdb", host="mongomock://localhost")

    # Run test method
    yield db

    # Tear down
    db.drop_database("testdb")
    disconnect()
