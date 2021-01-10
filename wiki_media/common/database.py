import os
from datetime import datetime

import databases
import sqlalchemy

from wiki_media.common import constants


class Database:
    def __init__(self, host: str, database: str, user: str, password: str):
        database_url = f"postgresql://{user}:{password}@{host}/{database}"
        self.database = databases.Database(database_url)

        metadata = sqlalchemy.MetaData()
        self.users = sqlalchemy.Table(
            "users",
            metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column("user", sqlalchemy.String),
            sqlalchemy.Column("bot", sqlalchemy.Boolean),
            sqlalchemy.Column("type", sqlalchemy.String),
            sqlalchemy.Column("title", sqlalchemy.String),
            sqlalchemy.Column("comment", sqlalchemy.String),
            sqlalchemy.Column("timestamp", sqlalchemy.Date)
        )
        engine = sqlalchemy.create_engine(database_url)
        metadata.create_all(engine)

    @classmethod
    def init(cls):
        return cls(os.environ.get("DB_URL", constants.DB_URL), constants.DB_DATABASE, "postgres", "postgres")

    async def connect(self):
        await self.database.connect()

    async def disconnect(self):
        await self.database.disconnect()

    async def get(self, user_id: str):
        query = self.users.select(whereclause=self.users.c.user == user_id)
        return await self.database.fetch_all(query)

    async def add(self, user: dict):
        if isinstance(user["timestamp"], int):
            user["timestamp"] = datetime.fromtimestamp(user["timestamp"])
        query = self.users.insert().values(**user)
        return await self.database.execute(query)
