 
import os
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from bedrock_context_embedding_client import EmbeddingPredictionClient


HOST = os.environ.get("HOST")
REGION= os.environ.get("REGION")
# host = 'duh8pbqxbazq9o5qkmm1.us-east-1.aoss.amazonaws.com'  # serverless collection endpoint, without https://
# region = 'us-east-1'  # e.g. us-east-1

service = 'aoss'
credentials = boto3.Session().get_credentials()

auth = AWSV4SignerAuth(credentials, REGION, service)

# create an opensearch client and use the request-signer
client = OpenSearch(
    hosts=[{'host': HOST, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20,
)

embeddingPredictionClient = EmbeddingPredictionClient()  


def lambda_handler(event, context):
  print(event)
  product_details = event[0]['payload']['value']
  ProductId = product_details["ProductId"]
  ProductImageUri = product_details["ProductImageGCSUri"]
  ProductDescription = product_details["ProductDescription"]
  ProductAttributes = product_details["ProductAttributes"]
  ProductImageIndexID = product_details["ProductImageIndexID"]
  ProductTextIndexID = product_details["ProductTextIndexID"]


  product_image_key = get_s3_key_from_uri(ProductImageUri)
  contextual_text = "Product Description: {} Product Attributes: {}".format(ProductDescription,ProductAttributes)

  embeddingsJson = embeddingPredictionClient.get_embeddings(s3_image_key=product_image_key,description=contextual_text, dimension=1024)
  try:
      text_document = {
        "context_index_id": ProductTextIndexID,
        "vector_embedding": embeddingsJson['text_embedding']
      }
      image_document = {
        "context_index_id": ProductImageIndexID,
        "vector_embedding": embeddingsJson['image_embedding']
      }
      print('Inserting vector into database')
      index_name = 'rag-index'
      text_response = client.index(
      index = index_name,
      body = text_document
      )
      print(text_response)
      image_response = client.index(
      index = index_name,
      body = image_document
      )
      print(image_response)
      return "Vector Stored Sucessfully"
  except Exception as e:
      print(e)
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
    
# product_attributes = "{\"product_attributes\": [{\"attribute_name\": \"Color\", \"attribute_value\": \"Blue\"}, {\"attribute_name\": \"Size\", \"attribute_value\": \"Medium\"}, {\"attribute_name\": \"Material\", \"attribute_value\": \"Cotton\"}, {\"attribute_name\": \"Pattern\", \"attribute_value\": \"Anarkali\"}]}"  
# product_image_uri = "s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg"
# product_id = 1100
# event =[{'payload': {'key': None, 'value': {'ProductId': product_id,'ProductImageIndexID':f'{product_id}_image','ProductTextIndexID':f'{product_id}_text', 'ProductDescription':'This a blue women anarkali dress','ProductImageGCSUri':product_image_uri , 'ProductAttributes':product_attributes }, 'timestamp': 1718264988578, 'topic': 'prompt', 'partition': 1, 'offset': 11}}]
# lambda_handler(event, 'context')