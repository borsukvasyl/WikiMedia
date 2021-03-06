WIKI_URL = "https://stream.wikimedia.org/v2/stream/recentchange"
API_URL = "localhost:8000"

# postgresql
DB_URL = "localhost:5432"
DB_DATABASE = "users"

# kafka
KAFKA_URL = "localhost:9092"
RAW_CHANNEL = "wiki"
USER_CHANNEL = "user"
USER_KEY = "user"
USER_VALUES = ["user", "bot", "type", "title", "comment", "timestamp"]
