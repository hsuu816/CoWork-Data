import redis
import json
import pymysql
import pymysql.cursors
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

mysql_host = os.environ.get('DB_HOST')
mysql_user = os.environ.get('DB_USERNAME')
mysql_password = os.environ.get('DB_PASSWORD')
mysql_database = os.environ.get('DB_DATABASE')

connection = pymysql.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database,
    cursorclass=pymysql.cursors.DictCursor
)

redis_client = redis.StrictRedis(host='0.0.0.0', port=6379, db=0)
stream_name = "bid_stream"


while True:
    stream_data = redis_client.xread({stream_name: "0"}, count=1)

    if stream_data:
        for stream, messages in stream_data:
            for message_id, message_data in messages:
                data = json.loads(message_data[b'event'])

                email = data['email']
                auction_id = data['auction_id']
                product_id = data['product_id']
                created_time = data['created_time']
                bid_price = data['bid_price']

                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO cowork.bid_history (auction_id, product_id, bid_price, email, created_time) VALUE (%s, %s, %s, %s, %s) ",
                                   (auction_id, product_id, bid_price, email, created_time))
                connection.commit()

                # 刪除已處理訊息
                redis_client.xdel(stream_name, message_id)

                print("Successfully inserted data into rds and deleted the message.")
