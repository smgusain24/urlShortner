import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from app.db import engine, links, init_db
import redis
from app.base62 import normalize_url, make_code_from_id
from dotenv import load_dotenv

from app.models import CreateOut, CreateIn

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

REDIS_URL = os.getenv("REDIS_URL")
cache = redis.Redis.from_url(REDIS_URL, decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/links", response_model=CreateOut, status_code=201)
def create_link(body: CreateIn):
    norm = normalize_url(str(body.long_url))

    with engine.begin() as conn:
        # 1) Insert or fetch existing row in one go
        row = conn.execute(
            text("""
                INSERT INTO links (long_url, normalized_url)
                VALUES (:raw, :norm)
                ON CONFLICT (normalized_url) DO UPDATE
                SET normalized_url = EXCLUDED.normalized_url
                RETURNING id, code
            """),
            {"raw": str(body.long_url), "norm": norm},
        ).mappings().one()

        row_id = int(row["id"])
        code = row["code"]

        # 2) If code not yet set (first time we see this URL), generate + persist it
        if code is None:
            code = make_code_from_id(row_id)
            conn.execute(
                text("UPDATE links SET code = :c WHERE id = :i AND code IS NULL"),
                {"c": code, "i": row_id},
            )

    return {"code": code, "short_url": f"{BASE_URL}/{code}"}


@app.get("/{code}")
def get_link(code: str):
    long_url = cache.get(code)
    if long_url:
        return RedirectResponse(long_url, status_code=301)
    with engine.begin() as conn:
        long_url = conn.execute(
            text("SELECT long_url FROM links WHERE code = :c"), {"c": code}
        ).scalar()
        if not long_url:
            raise HTTPException(status_code=404, detail="Not Found!")
        cache.set(code, long_url)
        return RedirectResponse(long_url, status_code=301)
