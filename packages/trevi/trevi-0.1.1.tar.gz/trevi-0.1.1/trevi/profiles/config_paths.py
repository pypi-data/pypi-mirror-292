class CONFIG_PATHS:
    class KAFKA:
        HOST = "kafka.host"
        PORT = "kafka.port"

    class REDIS:
        HOST = "redis.host"
        PORT = "redis.port"

    class TRADIER:
        BASE_URL = "external.tradier.base_url"
        ACCESS_TOKEN = "external.tradier.access_token"
        ACCOUNT_ID = "external.tradier.account_id"

    class ALPACA:
        BASE_URL = "external.alpaca.base_url"
        API_KEY = "external.alpaca.api_key"
        SECRET_KEY = "external.alpaca.secret_key"

    class COINBASE:
        API_KEY = "external.coinbase.api_key"
        SECRET_KEY = "external.coinbase.secret_key"

    class EVENT:
        KAFKA_TOPIC = "events.kafka.topic"

    class ORDER:
        class KAFKA:
            class TOPICS:
                PLACED = "orders.kafka.topics.placed"
                FILLED = "orders.kafka.topics.filled"

    class CLOCK:
        KAFKA_TOPIC = "clock.kafka.topic"
