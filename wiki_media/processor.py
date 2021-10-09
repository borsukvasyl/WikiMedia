import json
import os

import faust

from wiki_media.common import constants
from wiki_media.common.database import Database

kafka_url = os.getenv("KAFKA_URL", constants.KAFKA_URL)
app = faust.App("wiki_media", broker=f"kafka://{kafka_url}")
raw_topic = app.topic(constants.RAW_CHANNEL)
database = Database.init()


@app.agent()
async def save_user(stream):
    await database.connect()
    async for data in stream:
        try:
            await database.add(data)
            app.logger.info(f"Saved user {data[constants.USER_KEY]}")
        except Exception as e:
            app.logger.error(f"Failed to save user: {e}")


@app.agent(sink=[save_user])
async def process_user(stream):
    async for data in stream:
        try:
            user_key = data[constants.USER_KEY]
            user_value = {key: data[key] for key in constants.USER_VALUES}
            await app.send(constants.USER_CHANNEL, key=user_key, value=user_value)
            app.logger.info(f"Processed user message {user_key}")
            yield user_value
        except Exception as e:
            app.logger.error(f"Failed to process user message: {e}")


@app.agent(raw_topic, sink=[process_user])
async def process_raw(stream):
    async for payload in stream:
        try:
            data = json.loads(payload)
            app.logger.info("Processed raw message")
            yield data
        except Exception as e:
            app.logger.error(f"Failed to decode raw message: {e}")


if __name__ == "__main__":
    app.main()
