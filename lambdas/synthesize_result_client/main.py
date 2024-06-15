import boto3
import logging
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import BedrockChat
from botocore.config import Config
from generate_prompt import generate_prompt
from models.model import HumanRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Initialize boto3 session, bedrock and client
try:
    session = boto3.session.Session()
    # Initialize S3 client
    s3_client = boto3.client('s3')

# Configure retry settings for boto3
    retry_config = Config(
        region_name='us-east-1',
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        }
    )

    boto3_bedrock_runtime = session.client("bedrock-runtime", config=retry_config)
    # Model configuration
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    model_kwargs = {
        "max_tokens": 2048,  # Corrected parameter name
        "temperature": 0.0,
        "top_k": 250,
        "top_p": 1,
        # "stop_sequences": ["\n\nHuman"],
    }
    model = BedrockChat(
            client=boto3_bedrock_runtime,
            model_id=model_id,
            model_kwargs=model_kwargs,
        )
    logger.info("Initialized BedrockChat model.")

    chain = ChatPromptTemplate.from_messages([("{prompt}")]) | model | StrOutputParser()
    logger.info("Initialized boto3 session and bedrock-runtime client.")
except Exception as e:
    logger.error(f"Error initializing boto3 client: {e}")
    raise

def get_response(humanRequest):
    
    # Initialize the model
    try:
        
        logger.info("Created the processing chain.")
        generated_prompt = generate_prompt(humanRequest,s3_client)
        
        response = chain.invoke({"prompt": generated_prompt})
        logger.info(f"Chain invoked successfully with generated prompt.")
        return response
    except Exception as e:
        logger.error(f"Error invoking chain: {e}")
        return None

def lambda_handler(event,context):
    try:
        payload_details = event[0]['payload']['value']
        # prompt_text = payload_details['prompt_text']
        # product_description = payload_details['product_description']
        # product_attributes = payload_details['product_attributes']
        # product_gcs_uri = payload_details['product_gcs_uri']
        # prompt_image_url = payload_details['prompt_image_url']
        print(payload_details)
        humanRequest = HumanRequest(
            prompt_text="I'm looking for a blue Kurta.",
            product_description=["This is blue Kurta", "This is blue Kurta", "This is blue Kurta", "This is blue Kurta", "This is blue Kurta"],
            product_attributes=["{\"product_attributes\": [{\"attribute_name\": \"Color\", \"attribute_value\": \"Blue\"}, {\"attribute_name\": \"Size\", \"attribute_value\": \"Medium\"}, {\"attribute_name\": \"Material\", \"attribute_value\": \"Cotton\"}, {\"attribute_name\": \"Pattern\", \"attribute_value\": \"Anarkali\"}]}", "{\"product_attributes\": [{\"attribute_name\": \"Color\", \"attribute_value\": \"Blue\"}, {\"attribute_name\": \"Size\", \"attribute_value\": \"Medium\"}, {\"attribute_name\": \"Material\", \"attribute_value\": \"Cotton\"}, {\"attribute_name\": \"Pattern\", \"attribute_value\": \"Anarkali\"}]}", "{\"product_attributes\": [{\"attribute_name\": \"Color\", \"attribute_value\": \"Blue\"}, {\"attribute_name\": \"Size\", \"attribute_value\": \"Medium\"}, {\"attribute_name\": \"Material\", \"attribute_value\": \"Cotton\"}, {\"attribute_name\": \"Pattern\", \"attribute_value\": \"Anarkali\"}]}", "{\"product_attributes\": [{\"attribute_name\": \"Color\", \"attribute_value\": \"Blue\"}, {\"attribute_name\": \"Size\", \"attribute_value\": \"Medium\"}, {\"attribute_name\": \"Material\", \"attribute_value\": \"Cotton\"}, {\"attribute_name\": \"Pattern\", \"attribute_value\": \"Anarkali\"}]}", "{\"product_attributes\": [{\"attribute_name\": \"Color\", \"attribute_value\": \"Blue\"}, {\"attribute_name\": \"Size\", \"attribute_value\": \"Medium\"}, {\"attribute_name\": \"Material\", \"attribute_value\": \"Cotton\"}, {\"attribute_name\": \"Pattern\", \"attribute_value\": \"Anarkali\"}]}"],
            product_gcs_uri=["s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg", "s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg", "s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg", "s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg", "s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg"],
            prompt_image_url="s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg"
        )
        response = get_response(humanRequest)
        if response:
            print(response)
    except Exception as e:
        logger.error(f"Error invoking chain: {e}")
        return None
event = [{'payload':{'value':1}}]
lambda_handler(event,'context')