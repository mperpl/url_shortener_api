from contextlib import asynccontextmanager
import sys
from typing import Union
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from database import DB_SESSION
from sqlalchemy import select, update
from database import async_create_db_tables, async_engine
from encoding import to_base62
import models
from normalize_url import normalize_url
import schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    if "pytest" not in sys.modules:
        await async_create_db_tables()
    yield
    await async_engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get('/')
async def root():
    return {'message': 'URL Shortener API'}


@app.get('/mappings', response_model=list[schemas.MappingsPrint])
async def get_mappings(request: Request, db: DB_SESSION):
    base_url = str(request.base_url).rstrip('/')

    result = await db.scalars(select(models.UrlMapping))
    mappings = result.all()

    return [
        {
            "id": m.id,
            "url": m.url,
            "short_code": m.short_code,
            "short_url": f"{base_url}/{m.short_code}",
            "clicks": m.clicks,
        }
        for m in mappings
    ]



@app.post('/shorten', response_model=Union[schemas.MappingsPrint, schemas.MappingsPrintDetail])
async def shortener(request: Request, payload: schemas.Url, db: DB_SESSION):
    base_url = str(request.base_url).rstrip('/')
    target_url = normalize_url(str(payload.url))

    result = await db.execute(
        select(models.UrlMapping).where(models.UrlMapping.url == target_url)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return {
            "id": existing.id,
            "url": existing.url,
            "short_code": existing.short_code,
            "short_url": f"{base_url}/{existing.short_code}",
            "clicks": existing.clicks,
            "detail": "The mapping already exists.",
        }

    try:
        new_mapping = models.UrlMapping(
            url=target_url,
            short_code=None,
        )

        db.add(new_mapping)

        await db.flush() 
        new_mapping.short_code = to_base62(new_mapping.id)

        await db.commit()
        await db.refresh(new_mapping)

        return {
            "id": new_mapping.id,
            "url": new_mapping.url,
            "short_code": new_mapping.short_code,
            "short_url": f"{base_url}/{new_mapping.short_code}",
            "clicks": new_mapping.clicks,
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    



@app.get('/{short_code}')
async def redirect(short_code: str, db: DB_SESSION):
    result = await db.execute(
        select(models.UrlMapping).where(models.UrlMapping.short_code == short_code)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found")

    await db.execute(
        update(models.UrlMapping)
        .where(models.UrlMapping.id == record.id)
        .values(clicks=models.UrlMapping.clicks + 1)
    )
    
    await db.commit()

    return RedirectResponse(url=record.url, status_code=307)

