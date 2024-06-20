from predict.bedrock_prompt_embedding_client import EmbeddingPredictionClient
from search.prompt_open_search_client import VectorSearchClient
from kafka.producer import run_producer
import os
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import logging
logger = logging.getLogger()
logger.setLevel("INFO")


KAFKA_TOPIC_NAME = os.environ.get("KAFKA_TOPIC_NAME")
KAFKA_API_KEY = os.environ.get("KAFKA_API_KEY")
KAFKA_API_SECRET = os.environ.get("KAFKA_API_SECRET")
REGION = os.environ.get("REGION")
BOOTSTRAP_KAFKA_SERVER = os.environ.get("BOOTSTRAP_KAFKA_SERVER")
SR_URL = os.environ.get("SR_URL")
SR_API_KEY = os.environ.get("SR_API_KEY")
SR_API_SECRET = os.environ.get("SR_API_SECRET")
HOST = os.environ.get("HOST")

SCHEMA_CONF =  {
            'url':SR_URL,
    'basic.auth.user.info':f'{SR_API_KEY}:{SR_API_SECRET}'
}

PRODUCER_CONF = {
        'bootstrap.servers': BOOTSTRAP_KAFKA_SERVER,
        'sasl.username': KAFKA_API_KEY,
        'sasl.password':KAFKA_API_SECRET
    }

credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, REGION, 'aoss')

# create an opensearch client and use the request-signer
os_client = OpenSearch(
    hosts=[{'host': HOST[8:], 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20,
)
embeddingPredictionClient = EmbeddingPredictionClient()   

vectorSearchClient = VectorSearchClient(os_client)

def lambda_handler(event, context):
    logger.info(event)
    try:
        prompt_details = event[0]['payload']['value']
        text = prompt_details['text']
        image_url = prompt_details['image_url']
        logger.info(prompt_details['prompt_id'])
        s3_image_key = get_s3_key_from_uri(image_url)
        embeddings = embeddingPredictionClient.get_embeddings(s3_image_key=s3_image_key,description=text, dimension=1024)
        logger.info(f"Received embeddings {embeddings}")
        matched_items = vectorSearchClient.query_vector_search(embeddings,1)
        logger.info(f"Received matched_items {matched_items}")
        response_text = run_producer(matched_items,prompt_details,PRODUCER_CONF,SCHEMA_CONF,KAFKA_TOPIC_NAME)
        return "Success"
    except Exception as e:
        logger.error(e)
        return e

def get_s3_key_from_uri(s3_uri):
    if s3_uri.startswith("s3://"):
        uri_without_prefix = s3_uri[5:]
        slash_pos = uri_without_prefix.find('/')
        if slash_pos != -1:
            key = uri_without_prefix[slash_pos+1:]
            return key
        else:
            raise ValueError("Invalid S3 URI format, no '/' found after bucket name")
    else:
        raise ValueError("Invalid S3 URI format, must start with 's3://'")

# event=[{'payload':{'value':{'prompt_id':'abcedrf','text':'Suggest me a similar dress','session_id':123,'image_url':'s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg'}}}]
# lambda_handler(event,'contxt')
