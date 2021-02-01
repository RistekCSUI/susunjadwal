import pytest
from mongoengine import disconnect, connect


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
