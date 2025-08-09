import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, BIGINT, String, Text, TIMESTAMP, func

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

meta = MetaData()

links = Table(
    "links", meta,
    Column("id", BIGINT, primary_key=True, autoincrement=True),
    Column("code", String(32), unique=True, index=True, nullable=True),
    Column("long_url", Text, nullable=False),
    Column("created_at", TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
)


def init_db():
    with engine.begin() as conn:
        meta.create_all(conn)

