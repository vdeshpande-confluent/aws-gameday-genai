
import sys
import os
from image_to_text import image_to_product_description,image_to_attributes
from contextproducer import setup_producer,run_producer
from images import list_images_in_bucket
import time
import sys
import boto3 
import logging
logger = logging.getLogger()
logger.setLevel("INFO")

# from dotenv import load_dotenv

# load_dotenv()

context_bucket = os.getenv('CONTEXT_BUCKET')
context_size = int(os.getenv('CONTEXT_SIZE'))
dataset_name = os.getenv('DATASET_NAME')
s3_client = boto3.client('s3')


class Context(object):
    def __init__(self, ProductImageIndexID, ProductDescription, ProductId, ProductImageGCSUri,ProductAttributes,ProductTextIndexID):
        self.ProductImageIndexID = ProductImageIndexID
        self.ProductDescription = ProductDescription
        self.ProductId = ProductId
        self.ProductImageGCSUri = ProductImageGCSUri
        self.ProductAttributes = ProductAttributes
        self.ProductTextIndexID = ProductTextIndexID

def lambda_handler(event,context):
    logger.info("Downloading the dataset from kaggle")
    images = list_images_in_bucket(context_bucket, "raw-dataset/images",s3_client,context_size)
    topic,producer,sr=setup_producer()
    logger.info(len(images))
    index = 1
    try:
        for image in images:
            logger.info(f"Genrating product attributes and description for image {image}")
            image_uri = image
            result_att = image_to_attributes(image_uri,s3_client)
            result_desc = image_to_product_description(image_uri,s3_client)
            data = Context(ProductId=index,ProductImageIndexID=f"{index}_image",ProductTextIndexID=f"{index}_text", ProductImageGCSUri=image_uri, ProductDescription=result_desc, ProductAttributes=result_att)
            logger.info(f"Running producer for product no {index}")
            run_producer(topic,producer,sr,str(data.ProductId),data)
            index+=1
    except Exception as e:
        logger.error("An unknown error occured:{}".format(e)) 
    producer.flush()



# logger.info("Application started")
# lambda_handler('event','context')
# logger.info("Application finished")

