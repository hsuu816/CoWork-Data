import redis
import time
import json
from server.utils.util import dir_last_updated


pool = redis.ConnectionPool(host='0.0.0.0', port=6379, db=0)

def connect_to_redis(pool):
    try:
        redis_client = redis.Redis(connection_pool=pool)
        print("Successfully connected to Redis!")
        return redis_client
    except redis.ConnectionError as e:
        print("Error connecting to Redis:", str(e))


def to_message_queue(broadcast_message):
    redis_client = connect_to_redis(pool)

    data = {
        "email": "wait",
        "auction_id": redis_client.get('auction_id').decode('utf-8'),
        "product_id": redis_client.get('product_id').decode('utf-8'),
        "created_time": int(time.time() * 1000),
        "bid_price": json.loads(broadcast_message)['number']
        # "start_bid": redis_client.get('start_bid'),
        # "end_time": redis_client.get('end_time')
    }

    print(data)