import requests
import base64
import json
import os
import logging
logger = logging.getLogger()
logger.setLevel("INFO")

bootstrap_server = os.environ.get("KAFKA_BOOTSTRAP_SERVER")[:-5]
cluster_id = os.environ.get("CLUSTER_ID")
topic_name = os.environ.get("KAFKA_TOPIC_NAME")
api_key= os.environ.get("KAFKA_API_KEY")
api_secret = os.environ.get("KAFKA_API_SECRET")

def produce_recommendation_result(prompt_id,response):
    try: 
        # Your Confluent Cloud API endpoint
        
        url = f'https://{bootstrap_server}/kafka/v3/clusters/{cluster_id}/topics/{topic_name}/records'
        
        # Encode your API key and secret
        credentials = f'{api_key}:{api_secret}'
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        # The headers including the authorization and content type
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
        # The data you want to send
        data = {
            "value": {
                "type": "JSON",
                "data": {"prompt_id":prompt_id,"product_recommendations": response}
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code!=200:
            raise Exception("Record not produced to recommendation topic, Error Code"+response.status_code+"Error response"+response.json())
    
        logger.info("Response successfully produce to recommendation topic:"+response.status_code)
        logger.info(response.json())
    except Exception as e:
        logger.error(e)