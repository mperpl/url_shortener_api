import models


def test_root(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'message': 'URL Shortener API'}


def test_get_mappings_empty(client, clean_db):
    response = client.get('/mappings')

    assert response.status_code == 200
    assert response.json() == []
    
def test_get_mappings(client, dummy_data):
    response = client.get('/mappings')

    assert response.status_code == 200
    assert response.json() == [
        {
            'id': 1,
            'url': 'https://www.youtube.com',
            'short_code': '1',
            'short_url': f'{client.base_url}/1',
            'clicks': 99
        },
        {
            'id': 2,
            'url': 'https://www.google.com',
            'short_code': '2',
            'short_url': f'{client.base_url}/2',
            'clicks': 99
        }
    ]


def test_shorten(client, clean_db):
    response1 = client.post('/shorten', json={"url": "https://example1.com"})
    response2 = client.post('/shorten', json={"url": "https://example2.com"})
    
    assert response1.status_code == 200
    assert response1.json() == {
        "id": 1,
        "url": 'https://example1.com',
        "short_code": '1',
        "short_url": f"{client.base_url}/1",
        "clicks": 0,
    }

    assert response2.status_code == 200
    assert response2.json() == {
        "id": 2,
        "url": 'https://example2.com',
        "short_code": '2',
        "short_url": f"{client.base_url}/2",
        "clicks": 0,
    }

def test_shorten_existing(client, dummy_data):
    response = client.post('/shorten', json={"url": "https://www.youtube.com"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "url": "https://www.youtube.com",
        "short_code": "1",
        "short_url": f"{client.base_url}/1",
        "clicks": 99,
        "detail": "The mapping already exists."
    }

def test_shorten_invalid_url(client, clean_db):
    response = client.post('/shorten', json={"url": ""})
    assert response.status_code == 422

    response = client.post('/shorten', json={"url": "htp:/invalid"})
    assert response.status_code == 422

def test_redirect_missing(client, clean_db):
    response = client.get('/1')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Short URL not found'}

def test_redirect(client, dummy_data, session):
    mapping = session.get(models.UrlMapping, 1)
    assert mapping.clicks == 99

    response = client.get('/1', follow_redirects=True)
    session.refresh(mapping)
    assert mapping.clicks == 100

    assert response.status_code == 200