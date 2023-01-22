import random, string

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from .db import DB


app = FastAPI()
database = DB()
app.add_event_handler("startup", database.get_engine)


class Url(BaseModel):
    long_url: str = None
    custom_slug: str = None


@app.get("/")
async def root():
    return 'Em construção, disponível públicamente em breve!'


@app.get("/{slug}")
async def redirect(slug: str):
    session = database.get_session()
    result = session.execute("SELECT long_url FROM url_data WHERE short_slug = %s", (slug,)).fetchone()
    if result is None:
        return {'detail': 'Not Found'}

    session.execute("UPDATE url_data SET clicks = clicks + 1 WHERE short_slug = %s", (slug,))    
    return RedirectResponse(result[0])


@app.post("/api/v1/create")
async def create(long_url: Url):
    session = database.get_session()
    if long_url.custom_slug is None:
        short_slug = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    else:
        short_slug = long_url.custom_slug.lower().strip().replace(' ', '-')

    session.execute("INSERT INTO url_data (short_slug, long_url) VALUES (%s, %s)", (short_slug, long_url.long_url))
    short_url = f'https://tabne.ws/{short_slug}'
    return {'short_slug': short_url}


@app.get("/api/v1/stats/{slug}")
def stats(slug: str):
    session = database.get_session()
    result = session.execute("SELECT clicks, long_url, created_at FROM url_data WHERE short_slug = %s", (slug,)).fetchone()
    if result is None:
        return {'detail': 'Not Found'}

    return {'clicks': result[0], 'short_slug': slug, 'long_url': result[1], 'created_at': result[2]}


