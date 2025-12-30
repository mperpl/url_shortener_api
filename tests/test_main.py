import pytest
import models
from sqlalchemy import select


@pytest.mark.asyncio
async def test_shorten_normalization(client):
    resp1 = await client.post('/shorten', json={"url": "https://example.com/"})
    data1 = resp1.json()

    resp2 = await client.post('/shorten', json={"url": "https://www.example.com/"})
    data2 = resp2.json()

    assert data1["id"] == data2["id"]
    assert data2["detail"] == "The mapping already exists."


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'URL Shortener API'}


@pytest.mark.asyncio
async def test_get_mappings_empty(client):
    response = await client.get('/mappings')
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_get_mappings(client, dummy_data):
    response = await client.get('/mappings')
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    assert data[0]['url'] == 'https://youtube.com'
    assert data[0]['short_code'] == '1'
    assert data[1]['url'] == 'https://google.com'


@pytest.mark.asyncio
async def test_shorten(client):
    response = await client.post('/shorten', json={"url": "https://example1.com"})
    data = response.json()
    
    assert response.status_code == 200
    assert data["url"] == "https://example1.com"
    assert "short_code" in data

@pytest.mark.asyncio
async def test_shorten_existing(client, dummy_data):
    response = await client.post('/shorten', json={"url": "https://youtube.com"})

    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == "1"
    assert data["detail"] == "The mapping already exists."

@pytest.mark.asyncio
async def test_shorten_invalid_url(client):
    response = await client.post('/shorten', json={"url": "htp:/invalid"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_redirect_missing(client):
    response = await client.get('/999')
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_redirect(client, dummy_data, session):
    response = await client.get('/1', follow_redirects=False)
    
    assert response.status_code == 307
    assert response.headers['location'] == 'https://youtube.com'

    
    result = await session.execute(
        select(models.UrlMapping).where(models.UrlMapping.short_code == '1')
    )
    mapping = result.scalar_one()
    assert mapping.clicks == 100