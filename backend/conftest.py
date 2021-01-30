import pytest
from mongoengine import disconnect, connect
from app import app
from app.utils import generate_token
from models.major import Major
from models.user import User


@pytest.fixture(scope='function')
def auth_client(mongo):
    """Generate authenticated test client,
    including test user and major for every function.
    Using test database through 'mongo' fixture.
    How to use this fixture for a method:
    ```
    def test_xxx(self, auth_client):
        client, user = auth_client
        # Use client to make request
        # Use user to obtain user id
    ```
    """
    print('~~~~ AUTH CLIENT ~~~~')
    with app.test_client() as client:
        with app.app_context():
            app.config.update(
                TESTING=True,
                ENV='test'
            )
            user, token = create_test_user()
        client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + token
        yield client, user


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


def create_test_user():
    major = Major.objects().create(
        name='Ilmu Komputer (Computer Science)',
        kd_org='01.00.12.01'
    )
    user = User.objects().create(
        name='NAMA USER',
        username='nama.user',
        npm='1701234567',
        batch='2017',
        major=major,
    )
    token = generate_token(user.id, user.major.id)
    return user, token
