import redis
import time
import json


pool = redis.ConnectionPool(host='0.0.0.0', port=6379, db=0)

def connect_to_redis(pool):
    try:
        redis_client = redis.Redis(connection_pool=pool)
        print("Successfully connected to Redis!")
        return redis_client
    except redis.ConnectionError as e:
        print("Error connecting to Redis:", str(e))

def prepare_data_to_message_queue(latest_price, email):
    r = connect_to_redis(pool)
    data = {
        "email": email,
        "auction_id": r.get('auction_id').decode('utf-8'),
        "product_id": r.get('product_id').decode('utf-8'),
        "created_time": int(time.time() * 1000),
        "bid_price": latest_price
    }

    event = json.dumps(data)
    print(event)
    r.xadd("bid_stream", {"event": event})
    return event

def bid_stream_reader():
    r = connect_to_redis(pool)
    last_id = '0'
    while True:
        events = r.xread({b"bid_stream": last_id}, count=10)
        for _, event_list in events:
            for event_id, event_data in event_list:
                event_data = json.loads(event_data[b'event'])
                return f"Message Q ID: {event_id}, Bid Detail: {event_data}"
                last_id = event_id

if __name__ == "__main__":
    bid_stream_reader()