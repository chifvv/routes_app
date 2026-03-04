import pytest
from app import app, db, Driver


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


def test_create_driver(client):
    response = client.post('/api/drivers', json={
        'name': 'Иванов И.И.',
        'car_type': 'big',
        'route_ids': '1,2,3',
        'no_trip_days': 'СБ,ВС'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'id' in data
    assert data['message'] == 'Driver created'


def test_get_drivers_empty(client):
    response = client.get('/api/drivers')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []


def test_get_drivers_sorted(client):
    client.post('/api/drivers', json={'name': 'Яковлев А.А.', 'car_type': 'small'})
    client.post('/api/drivers', json={'name': 'Алексеев Б.Б.', 'car_type': 'big'})
    client.post('/api/drivers', json={'name': 'Петров В.В.', 'car_type': 'small'})
    
    response = client.get('/api/drivers')
    data = response.get_json()
    assert len(data) == 3
    assert data[0]['name'] == 'Алексеев Б.Б.'
    assert data[1]['name'] == 'Петров В.В.'
    assert data[2]['name'] == 'Яковлев А.А.'


def test_driver_appears_in_list_after_create(client):
    response = client.get('/api/drivers')
    data = response.get_json()
    assert len(data) == 0
    
    client.post('/api/drivers', json={
        'name': 'Новый Водитель',
        'car_type': 'big',
        'route_ids': '1,2'
    })
    
    response = client.get('/api/drivers')
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'Новый Водитель'


def test_multiple_drivers_multiple_fields(client):
    drivers = [
        {'name': 'Водитель 1', 'car_type': 'big', 'route_ids': '1,2,3', 'no_trip_days': 'СБ'},
        {'name': 'Водитель 2', 'car_type': 'small', 'route_ids': '4,5', 'no_trip_days': 'СБ,ВС'},
        {'name': 'Водитель 3', 'car_type': 'big', 'route_ids': '', 'no_trip_days': ''},
    ]
    for d in drivers:
        client.post('/api/drivers', json=d)
    
    response = client.get('/api/drivers')
    data = response.get_json()
    assert len(data) == 3
    
    assert data[0]['route_ids'] == '1,2,3'
    assert data[0]['no_trip_days'] == 'СБ'
    assert data[1]['car_type'] == 'small'
    assert data[2]['route_ids'] == ''


def test_update_driver(client):
    client.post('/api/drivers', json={'name': 'Тестов', 'car_type': 'small'})
    
    response = client.get('/api/drivers')
    data = response.get_json()
    driver_id = data[0]['id']
    
    response = client.put(f'/api/drivers/{driver_id}', json={
        'name': 'Тестов А.А.',
        'car_type': 'big',
        'route_ids': '1,2',
        'no_trip_days': 'ПН'
    })
    assert response.status_code == 200
    
    response = client.get('/api/drivers')
    data = response.get_json()
    assert data[0]['name'] == 'Тестов А.А.'
    assert data[0]['car_type'] == 'big'
    assert data[0]['route_ids'] == '1,2'
    assert data[0]['no_trip_days'] == 'ПН'


def test_update_not_found(client):
    response = client.put('/api/drivers/999', json={'name': 'Тест'})
    assert response.status_code == 404


def test_delete_driver(client):
    client.post('/api/drivers', json={'name': 'Удалить', 'car_type': 'small'})
    
    response = client.get('/api/drivers')
    data = response.get_json()
    driver_id = data[0]['id']
    
    response = client.delete(f'/api/drivers/{driver_id}')
    assert response.status_code == 200
    
    response = client.get('/api/drivers')
    data = response.get_json()
    assert len(data) == 0


def test_delete_not_found(client):
    response = client.delete('/api/drivers/999')
    assert response.status_code == 404


def test_random_driver_delete(client):
    client.post('/api/drivers', json={'name': 'Водитель 1', 'car_type': 'big'})
    client.post('/api/drivers', json={'name': 'Водитель 2', 'car_type': 'small'})
    client.post('/api/drivers', json={'name': 'Водитель 3', 'car_type': 'big'})
    
    response = client.get('/api/drivers')
    data = response.get_json()
    assert len(data) == 3
    
    driver_id_to_delete = data[1]['id']
    
    response = client.delete(f'/api/drivers/{driver_id_to_delete}')
    assert response.status_code == 200
    
    response = client.get('/api/drivers')
    data = response.get_json()
    assert len(data) == 2
    
    remaining_ids = [d['id'] for d in data]
    assert driver_id_to_delete not in remaining_ids


def test_driver_fields_match(client):
    client.post('/api/drivers', json={
        'name': 'Петров П.П.',
        'car_type': 'big',
        'route_ids': '1,2,3,4,5',
        'no_trip_days': 'ПН,ВТ,СР'
    })
    
    response = client.get('/api/drivers')
    data = response.get_json()
    
    driver = data[0]
    assert driver['name'] == 'Петров П.П.'
    assert driver['car_type'] == 'big'
    assert driver['route_ids'] == '1,2,3,4,5'
    assert driver['no_trip_days'] == 'ПН,ВТ,СР'


def test_driver_default_values(client):
    client.post('/api/drivers', json={'name': 'Минимальный'})
    
    response = client.get('/api/drivers')
    data = response.get_json()
    
    driver = data[0]
    assert driver['name'] == 'Минимальный'
    assert driver['car_type'] == 'small'
    assert driver['route_ids'] == ''
    assert driver['no_trip_days'] == ''
