from typing import Optional
import json
import boto3
import base64
import logging
import os
logger = logging.getLogger()
logger.setLevel("INFO")


bedrock_client = boto3.client('bedrock-runtime',region_name='us-east-1')
boto3_session = boto3.session.Session()
region_name = boto3_session.region_name    
s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get("BUCKET_NAME")

class EmbeddingPredictionClient:

    def __init__(self):
        pass
    
    def get_embeddings(self,
        s3_image_key:str,  
        description:str, 
        dimension:int=1024,
        model_id:str="amazon.titan-embed-image-v1"
        ):
        payload_body_text = {}
        payload_body_image = {}
        embedding_config = {
            "embeddingConfig": { 
                "outputEmbeddingLength": dimension
            }
        }

        if s3_image_key:
            image_object = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_image_key)
            image_content = image_object['Body'].read()
            encoded_image = base64.b64encode(image_content).decode('utf-8')
            payload_body_image["inputImage"] = encoded_image

        if description:
            payload_body_text["inputText"] = description


        logger.info("\n".join(payload_body_image.keys()))
        logger.info("\n".join(payload_body_text.keys()))

        response_text = bedrock_client.invoke_model(
            body=json.dumps({**payload_body_text, **embedding_config}), 
            modelId=model_id,
            accept="application/json", 
            contentType="application/json"
        )
        response_image = bedrock_client.invoke_model(
            body=json.dumps({**payload_body_image, **embedding_config}), 
            modelId=model_id,
            accept="application/json", 
            contentType="application/json"
        )
        response_text = json.loads(response_text.get("body").read())
        response_image = json.loads(response_image.get("body").read())
        embeddingsJson = {
            'image_embedding' :response_image["embedding"],
            'text_embedding':response_text["embedding"]
            }
        return embeddingsJson
