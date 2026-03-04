import pytest
from app import app, db, Route


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_create_route(client):
    response = client.post('/api/routes', json={
        'name': 'Test route',
        'price': 3000,
        'monday': True,
        'tuesday': False,
        'wednesday': True,
        'thursday': False,
        'friday': True,
        'saturday': False,
        'sunday': False
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'id' in data
    assert data['message'] == 'Route created'


def test_get_routes_empty(client):
    response = client.get('/api/routes')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []


def test_get_routes_sorted(client):
    client.post('/api/routes', json={'name': 'Яблоко', 'price': 1000})
    client.post('/api/routes', json={'name': 'Апельсин', 'price': 2000})
    client.post('/api/routes', json={'name': 'Банан', 'price': 1500})
    
    response = client.get('/api/routes')
    data = response.get_json()
    assert len(data) == 3
    assert data[0]['name'] == 'Апельсин'
    assert data[1]['name'] == 'Банан'
    assert data[2]['name'] == 'Яблоко'


def test_multiple_routes_multiple_days(client):
    client.post('/api/routes', json={
        'name': 'Маршрут 1',
        'price': 1000,
        'monday': True, 'tuesday': True, 'wednesday': True,
        'thursday': True, 'friday': True, 'saturday': False, 'sunday': False
    })
    client.post('/api/routes', json={
        'name': 'Маршрут 2',
        'price': 2000,
        'monday': False, 'tuesday': False, 'wednesday': True,
        'thursday': True, 'friday': True, 'saturday': True, 'sunday': True
    })
    
    response = client.get('/api/routes')
    data = response.get_json()
    assert len(data) == 2
    
    r1 = data[0]
    assert r1['monday'] == True
    assert r1['saturday'] == False
    
    r2 = data[1]
    assert r2['wednesday'] == True
    assert r2['sunday'] == True


def test_update_route(client):
    client.post('/api/routes', json={'name': 'Старое', 'price': 1000})
    
    response = client.get('/api/routes')
    data = response.get_json()
    route_id = data[0]['id']
    
    response = client.put(f'/api/routes/{route_id}', json={
        'name': 'Новое',
        'price': 2500,
        'monday': True
    })
    assert response.status_code == 200
    
    response = client.get('/api/routes')
    data = response.get_json()
    assert data[0]['name'] == 'Новое'
    assert data[0]['price'] == 2500
    assert data[0]['monday'] == True


def test_update_not_found(client):
    response = client.put('/api/routes/999', json={'name': 'Test'})
    assert response.status_code == 404


def test_delete_route(client):
    client.post('/api/routes', json={'name': 'Удалить', 'price': 1000})
    
    response = client.get('/api/routes')
    data = response.get_json()
    route_id = data[0]['id']
    
    response = client.delete(f'/api/routes/{route_id}')
    assert response.status_code == 200
    
    response = client.get('/api/routes')
    data = response.get_json()
    assert len(data) == 0


def test_delete_not_found(client):
    response = client.delete('/api/routes/999')
    assert response.status_code == 404


def test_random_route_delete(client):
    client.post('/api/routes', json={'name': 'Маршрут 1', 'price': 1000})
    client.post('/api/routes', json={'name': 'Маршрут 2', 'price': 2000})
    client.post('/api/routes', json={'name': 'Маршрут 3', 'price': 3000})
    
    response = client.get('/api/routes')
    data = response.get_json()
    assert len(data) == 3
    
    route_id_to_delete = data[1]['id']
    
    response = client.delete(f'/api/routes/{route_id_to_delete}')
    assert response.status_code == 200
    
    response = client.get('/api/routes')
    data = response.get_json()
    assert len(data) == 2
    
    remaining_ids = [r['id'] for r in data]
    assert route_id_to_delete not in remaining_ids


def test_route_fields_match(client):
    client.post('/api/routes', json={
        'name': 'Тест',
        'price': 5000,
        'monday': True,
        'tuesday': False,
        'wednesday': True,
        'thursday': False,
        'friday': True,
        'saturday': False,
        'sunday': False
    })
    
    response = client.get('/api/routes')
    data = response.get_json()
    
    route = data[0]
    assert route['name'] == 'Тест'
    assert route['price'] == 5000
    assert route['monday'] == True
    assert route['tuesday'] == False
    assert route['wednesday'] == True
    assert route['thursday'] == False
    assert route['friday'] == True
    assert route['saturday'] == False
    assert route['sunday'] == False


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'route' in response.data.lower() or b'html' in response.data.lower()
