import pytest
from app import app, get_db_connection

@pytest.fixture
def client():
    """Фикстура для тестирования Flask-приложения"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("TRUNCATE TABLE transactions, user_info RESTART IDENTITY CASCADE;")
                cursor.execute("TRUNCATE TABLE bonus_levels RESTART IDENTITY CASCADE;")
                
                cursor.execute("""
                    INSERT INTO bonus_levels (name, min_spendings, cashback_percentage)
                    VALUES ('Bronze', 0, 5), ('Silver', 500, 10), ('Gold', 1000, 15);
                """)
                conn.commit()
            finally:
                cursor.close()
                conn.close()
        yield client

def test_register_user(client):
    """Тест регистрации нового пользователя"""
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'securepassword'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'token' in data
    assert 'user_id' in data

def test_login_user(client):
    """Тест аутентификации пользователя"""
    client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'securepassword'
    })
    
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'securepassword'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data

def test_get_user_bonus(client):
    """Тест получения текущего бонусного уровня"""
    register_response = client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'securepassword'
    })
    token = register_response.get_json()['token']
    user_id = register_response.get_json()['user_id']
    
    response = client.get(f'/users/{user_id}/bonus', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Bronze'
    assert data['cashback_percentage'] == 5

def test_add_transaction(client):
    """Тест добавления транзакции и обновления уровня бонусов"""
    register_response = client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'securepassword'
    })
    token = register_response.get_json()['token']
    user_id = register_response.get_json()['user_id']
    
    response = client.post(f'/users/{user_id}/transactions', headers={
        'Authorization': f'Bearer {token}'
    }, json={
        'amount': 600 
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['new_spendings'] == 600
    assert data['bonus_update'] == 'Bonus level updated'

    bonus_response = client.get(f'/users/{user_id}/bonus', headers={
        'Authorization': f'Bearer {token}'
    })
    bonus_data = bonus_response.get_json()
    assert bonus_data['name'] == 'Silver'
    assert bonus_data['cashback_percentage'] == 10