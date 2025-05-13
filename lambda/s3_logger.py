import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    record = event['Records'][0]['s3']
    bucket = record['bucket']['name']
    key = record['object']['key']
    msg = f"New file uploaded: {key} in bucket: {bucket}"
    logger.info(msg)
    return {
        "statusCode": 200,
        "body": json.dumps(msg)
    }
