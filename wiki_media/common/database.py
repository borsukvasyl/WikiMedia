import os
from datetime import datetime

import databases
import dateutil.parser
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
            sqlalchemy.Column("timestamp", sqlalchemy.DateTime)
        )
        engine = sqlalchemy.create_engine(database_url)
        metadata.create_all(engine)

    @classmethod
    def init(cls):
        return cls(os.getenv("DB_URL", constants.DB_URL), constants.DB_DATABASE, "postgres", "postgres")

    async def connect(self):
        await self.database.connect()

    async def disconnect(self):
        await self.database.disconnect()

    async def get(self, user_id: str, page: int = 0, page_size: int = 25):
        query = self.users.select(
            whereclause=self.users.c.user == user_id
        ).limit(page_size).offset(page * page_size)
        return await self.database.fetch_all(query)

    async def add(self, user: dict):
        if isinstance(user["timestamp"], int):
            user["timestamp"] = datetime.utcfromtimestamp(user["timestamp"])
        query = self.users.insert().values(**user)
        return await self.database.execute(query)

    async def get_user_topics(self, user_id: str, n: int = 1):
        return await self.database.fetch_all(
            "SELECT title, COUNT(*) AS count "
            "FROM users "
            "WHERE \"user\" = :user_id "
            "GROUP BY title "
            "ORDER BY count DESC "
            "LIMIT :n",
            values={"user_id": user_id, "n": n}
        )

    async def get_user_contribution(self, user_id: str):
        return await self.database.fetch_all(
            "SELECT type, COUNT(*) as count "
            "FROM users "
            "WHERE \"user\" = :user_id "
            "GROUP BY type",
            values={"user_id": user_id}
        )

    async def get_top_user(self, time: str):
        return await self.database.fetch_one(
            "SELECT \"user\", COUNT(*) AS count "
            "FROM users "
            "WHERE timestamp >= :time "
            "GROUP BY \"user\" "
            "ORDER BY count DESC "
            "LIMIT 1",
            values={"time": dateutil.parser.parse(time)}
        )

    async def get_top_topics(self, n: int = 10):
        return await self.database.fetch_all(
            "SELECT title, COUNT(*) AS count "
            "FROM users "
            "WHERE type = 'edit' "
            "GROUP BY title "
            "ORDER BY count DESC "
            "LIMIT :n",
            values={"n": n}
        )
