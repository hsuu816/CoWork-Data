import re
import pymysql  
import pymysql.cursors
from urllib.parse import unquote
from collections import defaultdict
import datetime
import time
from dotenv import load_dotenv
import os
import pandas as pd
from google.cloud import bigquery

load_dotenv(verbose=True)

mysql_host = os.environ.get('DB_HOST')
mysql_user = os.environ.get('DB_USERNAME')
mysql_password = os.environ.get('DB_PASSWORD')
mysql_database = os.environ.get('DB_DATABASE')


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/yuchenhsiao/Downloads/neural-orbit-396702-8a069fa1cf45.json" 
bg_client = bigquery.Client()
DATASET_NAME = os.getenv("DATASET_NAME")

connection = pymysql.connect(
    host = mysql_host,
    user = mysql_user,
    password = mysql_password,
    database = mysql_database,
    cursorclass = pymysql.cursors.DictCursor
)


def get_product_table():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM product")
        results = cursor.fetchall()
        data = []
        for result in results:
            data.append(list(result.values()))
        dataframe = pd.DataFrame(data, columns=results[0].keys())
        return dataframe


def get_event_table(last_ts):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM tracking_user_event WHERE created_time > {last_ts}")
        results = cursor.fetchall()
        data = []
        for result in results:
            result
            data.append(list(result.values()))
        if data:
            dataframe = pd.DataFrame(data, columns=results[0].keys())
            return dataframe
        else:
            return None


def upload_to_bigquery(dataframe, table_name):
    job = bg_client.load_table_from_dataframe(dataframe=dataframe, destination=f"{DATASET_NAME}.{table_name}")
    job.result()
    print(f"{job.state}")


def update_event_table():
    last_ts = None
    while True:
        if last_ts is None:
            with connection.cursor() as cursor:
                cursor.execute("SELECT created_time FROM tracking_user_event limit 1")
                result = cursor.fetchone()
                last_ts = int(result['created_time'])-1
        dataframe = get_event_table(last_ts)
        if dataframe is not None:
            last_ts = int(dataframe.iloc[-1]['created_time'])
            dataframe['created_time_tw'] = dataframe['created_time'].apply(lambda ts: datetime.datetime.fromtimestamp(ts // 1000))
            upload_to_bigquery(dataframe, "tracking_user_event")
        time.sleep(5)


if __name__ == "__main__":
    update_event_table()

