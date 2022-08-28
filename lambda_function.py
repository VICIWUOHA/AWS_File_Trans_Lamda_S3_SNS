import urllib
from datetime import datetime as dt
from io import StringIO
import boto3
import json
import pandas as pd

year = dt.now().year
month = dt.strftime(dt.now(), '%B')
day = dt.now().day

def lambda_handler(event, context):

    s3 = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    # Get Bucket Name
    bucket = event['Records'][0]['s3']['bucket']['name']

    # Get the File Key
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding = 'utf-8')

    try:

        # Get the file from s3

        response = s3.get_object(Bucket = bucket, Key = key)

        # deserialize the  json object

        text = response["Body"].read().decode()
        data = json.loads(text)

        # preview the data

        print(data)

        transactions = data['transactions']
        for record in transactions:
            print(record['transType'])

        # normalize json and write to s3 object
        transformed_data = pd.json_normalize(transactions)

        # write to buffer memory
        csv_buffer = StringIO()
        transformed_data.to_csv(csv_buffer)

        # write to processed folder in s3

        s3_resource.Object(bucket, f"processed/transactions_{year}_{month}_{day}.csv").put(Body=csv_buffer.getvalue())
        print('Successfully Written to processed staging zone')
    
    except Exception as e:
        print(e)
        raise e
          
    return "Success"

