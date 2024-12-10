import pytest
from app import app  

@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_cursor

def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"VEHICLE RENTAL SYSTEM MANAGEMENT" in response.data

# TESTING ON CUSTOMER
def test_get_customers_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/customers')
    
    assert response.status_code == 404
    assert b"No customers found" in response.data

def test_get_customers(mock_db):
    mock_db.fetchall.return_value = [(1, 'John Doe', 'john.doe@example.com')]
    
    client = app.test_client()
    response = client.get('/customers')
    
    assert response.status_code == 200
    assert b"John Doe" in response.data
    assert b"john.doe@example.com" in response.data

def test_post_customer_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/customers', json={}) 
    
    assert response.status_code == 400

def test_post_customer_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.post('/customers', json={
        'customer_name': 'Ronald', 'customer_contact': 'ronald@gmail.com'
    })
    
    assert b"Customer created successfully", "customer_id" in response.data

def test_put_customer_missing_fields(mock_db):
    client = app.test_client()
    response = client.put('/customers/1', json={}) 
    
    assert response.status_code == 400
    assert b"Customer name is required and must be a valid string" in response.data

def test_put_customer_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.put('/customers/1', json={'customer_name': 'Updated Name', 'customer_contact': 'updated@example.com'})

    assert b"Customer updated successfully" in response.data

def test_delete_customer_not_found(mock_db):
    mock_db.rowcount = 0  
    
    client = app.test_client()
    response = client.delete('/customers/999')
    
    assert response.status_code == 404
    assert b"Customer not found" in response.data

def test_delete_customer_success(mock_db):
    mock_db.rowcount = 1  
    
    client = app.test_client()
    response = client.delete('/customers/1')
    
    assert b"Customer deleted successfully" in response.data

# TESTING ON VEHICLE
def test_get_vehicles_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/vehicles')
    
    assert response.status_code == 404
    assert b"No vehicles found" in response.data

def test_get_vehicles(mock_db):
    mock_db.fetchall.return_value = [
        (1, 'ABC123', 'Toyota Corolla', 50.00, 'Car')
    ]
    
    client = app.test_client()
    response = client.get('/vehicles')
    
    assert response.status_code == 200
    assert b"Toyota Corolla" in response.data

def test_post_vehicle_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/vehicles', json={}) 
    
    assert response.status_code == 400

def test_post_vehicle_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.post('/vehicles', json={
        'reg_number': 'FSA123', 'model_name': 'Mirage', 'daily_hire_rate': 50.00, 'vehicle_type': 'Sedan'
    })
    
    assert b"Vehicle created successfully", "vehicle_id" in response.data

def test_put_vehicle_missing_fields(mock_db):
    client = app.test_client()
    response = client.put('/vehicles/1', json={}) 
    
    assert response.status_code == 400
    assert b"Registration number is required and must be a valid string" in response.data

def test_put_vehicle_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.put('/vehicles/1', json={
        'reg_number': 'FSA123', 'model_name': 'Updated Mirage', 'daily_hire_rate': 50.00, 'vehicle_type': 'Sedan'
    })

    assert b"Vehicle updated successfully" in response.data

def test_delete_vehicle_not_found(mock_db):
    mock_db.rowcount = 0  
    
    client = app.test_client()
    response = client.delete('/vehicles/999')
    
    assert response.status_code == 404
    assert b"Vehicle not found" in response.data

def test_delete_vehicle_success(mock_db):
    mock_db.rowcount = 1  
    
    client = app.test_client()
    response = client.delete('/vehicles/1')
    
    assert b"Vehicle deleted successfully" in response.data

# TESTING ON LOCATIONS

def test_get_locations_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/locations')
    
    assert response.status_code == 404
    assert b"No locations found" in response.data

def test_get_locations(mock_db):
    mock_db.fetchall.return_value = [
        (1, 'Kampala', 1, 'True')
    ]
    
    client = app.test_client()
    response = client.get('/locations')
    
    assert response.status_code == 200
    assert b"Kampala" in response.data

def test_post_location_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/locations', json={}) 
    
    assert response.status_code == 400

def test_post_location_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.post('/locations', json={
        'location_name': 'Kampala', 'vehicle_id': 1, 'is_available': 'True'
    })
    
    assert b"Location created successfully", "location_id" in response.data

def test_put_location_missing_fields(mock_db):
    client = app.test_client()
    response = client.put('/locations/1', json={}) 
    
    assert response.status_code == 400
    assert b"Location name is required and must be a valid string" in response.data

def test_put_location_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.put('/locations/1', json={
        'location_name': 'Updated Kampala', 'vehicle_id': 1, 'is_available': 'True'
    })

    assert b"Location updated successfully" in response.data

def test_delete_location_not_found(mock_db):
    mock_db.rowcount = 0  
    
    client = app.test_client()
    response = client.delete('/locations/999')
    
    assert response.status_code == 404
    assert b"Location not found" in response.data

def test_delete_location_success(mock_db):
    mock_db.rowcount = 1  
    
    client = app.test_client()
    response = client.delete('/locations/1')
    
    assert b"Location deleted successfully" in response.data

# TESTING ON RENTALS

def test_get_rentals_empty(mock_db):
    mock_db.fetchall.return_value = []
    
    client = app.test_client()
    response = client.get('/rentals')
    
    assert response.status_code == 404
    assert b"No rentals found" in response.data

def test_get_rentals(mock_db):
    mock_db.fetchall.return_value = [
        (1, 1, 1, '2021-09-01', '2021-09-02', 100.00)
    ]
    client = app.test_client()
    response = client.get('/rentals')
    
    assert response.status_code == 200
    assert b"2021-09-01" in response.data

def test_post_rental_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/rentals', json={}) 
    
    assert response.status_code == 400

def test_post_rental_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.post('/rentals', json={
        'customer_id': 1, 'vehicle_id': 1, 'date_from': '2021-09-01', 'date_to': '2021-09-02', 'total_cost': 100.00
    })
    
    assert b"Rental created successfully", "rental_id" in response.data

def test_put_rental_missing_fields(mock_db):
    client = app.test_client()
    response = client.put('/rentals/1', json={}) 
    
    assert response.status_code == 400
    assert b"Customer ID is required and must be a valid integer" in response.data

def test_put_rental_success(mock_db):
    mock_db.rowcount = 1 
    
    client = app.test_client()
    response = client.put('/rentals/1', json={
        'customer_id': 1, 'vehicle_id': 1, 'date_from': '2021-09-01', 'date_to': '2021-09-02', 'total_cost': 100.00
    })

    assert b"Rental updated successfully" in response.data

def test_delete_rental_not_found(mock_db):
    mock_db.rowcount = 0  
    
    client = app.test_client()
    response = client.delete('/rentals/999')
    
    assert response.status_code == 404
    assert b"Rental not found" in response.data

def test_delete_rental_success(mock_db):
    mock_db.rowcount = 1  
    
    client = app.test_client()
    response = client.delete('/rentals/1')
    
    assert b"Rental deleted successfully" in response.data

if __name__ == "__main__":
    pytest.main()