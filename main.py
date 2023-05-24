from fastapi import FastAPI
from functools import lru_cache
from pydantic import BaseSettings
from psycopg_pool import ConnectionPool, AsyncConnectionPool
from psycopg.rows import dict_row

app = FastAPI()

class Settings(BaseSettings):
    db_host: str
    db_name: str
    db_user: str
    db_password: str
    db_port: str

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()

settings = get_settings()

conninfo = f"dbname={settings.db_name} user={settings.db_user} password={settings.db_password} port={settings.db_port} host={settings.db_host}"

pool = ConnectionPool(conninfo=conninfo, kwargs={"row_factory": dict_row})
async_pool = AsyncConnectionPool(conninfo=conninfo, kwargs={"row_factory": dict_row})


@app.post("/load")
def load():
    with pool.connection() as conn:
        for _ in range(100):
            conn.execute("insert into note (content) values ('hello world')")


@app.get("/notes")
def get_notes():
    with pool.connection() as conn:
        cur = conn.execute("select * from note")
        records = cur.fetchall()
        return records


@app.get("/async_notes")
async def get_async_notes():
    async with async_pool.connection() as conn:
        cur = await conn.execute("select * from note")
        records = await cur.fetchall()
        return records


@app.get("/")
def read_root():
    return {"Hello": "World"}
