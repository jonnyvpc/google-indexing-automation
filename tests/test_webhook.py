import pytest
from webhook_listener import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'uptime_seconds' in data
    assert 'timestamp' in data

def test_webhook_invalid_payload(client):
    """Test webhook with invalid payload"""
    response = client.post('/webhook', 
                         json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid payload'

def test_webhook_valid_payload(client, mocker):
    """Test webhook with valid payload"""
    # Mock the Google Indexing API call
    mock_service = mocker.Mock()
    mock_publish = mocker.Mock()
    mock_publish.execute.return_value = {
        'urlNotificationMetadata': {
            'url': 'https://jonnyvpc.com/news-posts/test-post'
        }
    }
    mock_service.urlNotifications.return_value.publish.return_value = mock_publish
    
    mocker.patch('webhook_listener.get_authenticated_service', 
                return_value=mock_service)

    response = client.post('/webhook',
                         json={'slug': 'test-post'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'request_id' in data
    assert 'response' in data

def test_webhook_authentication_error(client, mocker):
    """Test webhook with authentication error"""
    mocker.patch('webhook_listener.get_authenticated_service',
                side_effect=Exception('Authentication failed'))

    response = client.post('/webhook',
                         json={'slug': 'test-post'})
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Authentication failed' in data['error']

def test_request_tracing(client):
    """Test request tracing functionality"""
    response = client.post('/webhook',
                         json={'slug': 'test-post'},
                         headers={'X-Request-ID': 'test-123'})
    data = json.loads(response.data)
    assert 'request_id' in data

def test_performance_metrics(client):
    """Test performance metrics in response"""
    response = client.get('/health')
    data = json.loads(response.data)
    assert 'uptime_seconds' in data
    assert float(data['uptime_seconds']) >= 0

def test_error_handling(client):
    """Test error handling and logging"""
    response = client.post('/webhook',
                         json={'invalid': 'payload'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
