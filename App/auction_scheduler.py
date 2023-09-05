import redis 
import pymysql.cursors
import time
from dotenv import load_dotenv
import os
import asyncio
import websockets
import json

load_dotenv(verbose=True)

mysql_host = os.environ.get('DB_HOST')
mysql_user = os.environ.get('DB_USERNAME')
mysql_password = os.environ.get('DB_PASSWORD')
mysql_database = os.environ.get('DB_DATABASE')

connection = pymysql.connect(
    host = mysql_host,
    user = mysql_user,
    password = mysql_password,
    database = mysql_database,
    cursorclass = pymysql.cursors.DictCursor
)


def get_auction_info():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM  management as m left join auction_product as a on m.auction_product_id = a.id limit 1")
        result = cursor.fetchone()
    return result


async def notify():
    url = "ws://127.0.0.1:9000/api/1.0/update_bid"
    async with websockets.connect(url) as websocket:
        data = json.dumps({
            "type": "trigger_notify_winner",
            "auction_id": r.get('auction_id'),
            "product_id": r.get('product_id')
        })
        await websocket.send(data)
        response = await websocket.recv()
        print(response)
        # Exiting the 'async with' block will close the connection

# data_dict = {}
# data_dict['auction_id'] = get_auction_info()['auction_id']
# data_dict['latest_price'] = get_auction_info()['start_bid']
# data_dict['end_time'] = get_auction_info()['end_time']

r = redis.Redis(host='localhost', port=6379, decode_responses=True)  
r.flushdb()

while True:
    if r.get('auction_id') is None:
        auction_id = get_auction_info()['auction_id']
        r.setnx('auction_id', auction_id)
        r.set('start_bid', get_auction_info()['start_bid'])
        r.set('end_time', get_auction_info()['end_time'])
        r.set('product_id', get_auction_info()['auction_product_id'])
        print(r.get('product_id'))
        with connection.cursor() as cursor:
            cursor.execute("UPDATE cowork.management SET status = 'going' where auction_id = %s", (auction_id,))
        connection.commit()
    if int(r.get('end_time')) < int(time.time()):
        auction_id = r.get('auction_id')
        with connection.cursor() as cursor:
            cursor.execute("UPDATE cowork.management SET status = 'successed' where auction_id = %s", (auction_id,))
        connection.commit()
        asyncio.get_event_loop().run_until_complete(notify())
        r.flushdb()

