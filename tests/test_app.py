import pytest
from app import create_app

@pytest.fixture
def client():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }

    app = create_app(test_config)

    with app.test_client() as client:
        with app.app_context():
            app.db.create_all()
            user1 = app.User(name='Alice')
            user2 = app.User(name='Bob')
            app.db.session.add_all([user1, user2])
            app.db.session.commit()
        yield client

def test_get_users(client):
    response = client.get('/users')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['name'] == 'Alice'
    assert data[1]['name'] == 'Bob'

