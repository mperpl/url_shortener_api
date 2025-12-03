from typing import Union
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from database import DB_SESSION
from sqlalchemy import select
from database import create_db_tables
from encoding import to_base62
import models
import schemas

app = FastAPI(title='URL Shortener API')
create_db_tables()

@app.get('/')
def root():
    return 'URL Shortener API'


@app.get('/mappings', response_model=list[schemas.MappingsPrint])
def get_mappings(http_request: Request, db: DB_SESSION):
    base_url = str(http_request.base_url).rstrip('/')
    
    mappings = db.scalars(select(models.UrlMapping)).all()
    response_data = []

    for mapping in mappings:
        response_data.append({
            "id": mapping.id,
            "url": mapping.url,
            "short_code": mapping.short_code,
            "short_url": f"{base_url}/{mapping.short_code}",
            "clicks": mapping.clicks
        })
    return response_data


@app.post('/shorten', response_model=Union[schemas.MappingsPrint, schemas.MappingsPrintDetail])
def shortener(http_request: Request, request: schemas.Url, db: DB_SESSION):
    base_url = str(http_request.base_url).rstrip('/')

    existing = db.execute(
        select(models.UrlMapping).where(models.UrlMapping.url == str(request.url).rstrip('/'))
    ).scalar_one_or_none()

    if existing:
        return {
            "id": existing.id,
            "url": existing.url,
            "short_code": existing.short_code,
            "short_url": f"{base_url}/{existing.short_code}",
            "clicks": existing.clicks,
            "detail": 'The mapping already exists.'
        }

    try:
        new_url_mapping = models.UrlMapping(url=str(request.url).rstrip('/'), short_code=None)
        db.add(new_url_mapping)
        db.flush()
        new_url_mapping.short_code = to_base62(new_url_mapping.id)
        db.commit()

        return {
            "id": new_url_mapping.id,
            "url": new_url_mapping.url,
            "short_code": new_url_mapping.short_code,
           "short_url": f"{base_url}/{new_url_mapping.short_code}",
            "clicks": new_url_mapping.clicks,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get('/{short_code}')
def redirect(short_code: str, db: DB_SESSION):

    record = db.execute(
        select(models.UrlMapping).where(models.UrlMapping.short_code == short_code)
    ).scalar_one_or_none()

    if record:
        record.clicks += 1
        db.commit()
        return RedirectResponse(url=record.url)
    raise HTTPException(status_code=404, detail="Short URL not found")
