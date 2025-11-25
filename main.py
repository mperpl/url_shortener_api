from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import create_db_tables, get_db
from encoding import to_base62
import models
import schemas

app = FastAPI(title='URL Shortener API')
create_db_tables()

@app.get('/')
def root():
    return 'URL Shortener API'


@app.get('/mappings')
def get_mappings(db: Session = Depends(get_db)):
    return db.query(models.UrlMapping).all()


@app.post('/shorten')
def shortener(http_request: Request, request: schemas.Url, db: Session = Depends(get_db)):
    UrlMapping = models.UrlMapping
    base_url = str(http_request.base_url)

    existing = db.execute(
        select(UrlMapping).where(UrlMapping.url == request.url)
    ).scalar_one_or_none()

    if existing:
        return {'short_url': base_url + existing.short_code}

    try:
        new_url = UrlMapping(url=request.url, short_code=None)
        db.add(new_url)
        db.flush()
        new_url.short_code = to_base62(new_url.id)
        db.commit()


        return {'short_url': base_url + new_url.short_code}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get('/{short_code}')
def redirect(short_code, db: Session = Depends(get_db)):
    UrlMapping = models.UrlMapping

    record = db.execute(
        select(UrlMapping).where(UrlMapping.short_code == short_code)
    ).scalar_one_or_none()

    if record:
        record.clicks += 1
        db.commit()
        return RedirectResponse(url=record.url)
    raise HTTPException(status_code=404, detail="Short URL not found")
