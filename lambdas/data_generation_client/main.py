
import sys
import os
from image_to_text import image_to_product_description,image_to_attributes
from contextproducer import setup_producer,run_producer
from upload_dataset import download_and_upload
from images import list_images_in_bucket
import logging
import time
import logging
import sys
import boto3 
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


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
    
    download_and_upload(dataset_name,context_size, context_bucket,s3_client)

    images = list_images_in_bucket(context_bucket, "raw-dataset/images",s3_client)
    index= len(images)-1
    topic,producer,sr=setup_producer()
    
    
    while index>0:
        """"
        Creating the product description and product attributes from the gcs uri
        """
        try:
            logger.info(f"Genrating product attributes and description for image {index}")
            t_s = time.time()
            image_uri = images[index]
            result_att = image_to_attributes(image_uri,s3_client)
            result_desc = image_to_product_description(image_uri,s3_client)
            data = Context(ProductId=index,ProductImageIndexID=f"{index}_image",ProductTextIndexID=f"{index}_text", ProductImageGCSUri=image_uri, ProductDescription=result_desc, ProductAttributes=result_att)
            logger.info(f"Running producer for product no {index}")
            run_producer(topic,producer,sr,str(data.ProductId),data)
            t_e = time.time()
            if 5>t_e-t_s>0:
                d = t_e - t_s
                time.sleep(5-d)
            index = index - 1
        except Exception as e:
            logger.info("An unknown error occured:{}".format(e))
    producer.flush()


logger.info("Application started")
lambda_handler('event','context')
logger.info("Application finished")

