import asyncio
import json
import os

import faust

from wiki_media.common import constants

kafka_url = os.environ.get("KAFKA_URL", constants.KAFKA_URL)
app = faust.App("wiki_media", broker=f"kafka://{kafka_url}")
raw_topic = app.topic(constants.RAW_CHANNEL)


@app.agent()
async def process_user(stream):
    async for data in stream:
        try:
            user_key = data[constants.USER_KEY]
            user_value = {key: data[key] for key in constants.USER_VALUES}
            await app.send(constants.USER_CHANNEL, key=user_key, value=user_value)
            app.logger.info(f"Processed user message {user_key}")
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
