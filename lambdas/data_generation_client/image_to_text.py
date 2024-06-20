import boto3
import json
import base64
import logging
logger = logging.getLogger()
logger.setLevel("INFO")


# Initialize AWS clients
bedrock_client = boto3.client('bedrock-runtime')


def get_encoded_image_from_uri(s3_uri, s3_client):
    try:
        if s3_uri.startswith("s3://"):
            uri_without_prefix = s3_uri[5:]
            slash_pos = uri_without_prefix.find('/')
            if slash_pos != -1:
                bucket_name = uri_without_prefix[:slash_pos]
                s3_image_key = uri_without_prefix[slash_pos+1:]
                image_object = s3_client.get_object(Bucket=bucket_name, Key=s3_image_key)
                image_content = image_object['Body'].read()
                encoded_image = base64.b64encode(image_content).decode('utf-8')
                return encoded_image
            else:
                raise ValueError("Invalid S3 URI format, no '/' found after bucket name")
        else:
            raise ValueError("Invalid S3 URI format, must start with 's3://'")
    except Exception as e:
        logger.error(f"Error encoding image from S3 URI: {e}")
        raise e

def content_generation(prompt: str, im):
    
    try:

        bedrock_runtime = boto3.client(service_name='bedrock-runtime')

        model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
        max_tokens = 2048
 
        message = {"role": "user",
             "content": [
                {"type": "image", "source": {"type": "base64",
                    "media_type": "image/jpeg", "data": im}},
                {"type": "text", "text": prompt}
                ]}

    
        messages = [message]

        response = run_multi_modal_prompt(bedrock_client, model_id, messages, max_tokens)
        


    except Exception as err:
        message = err.response["Error"]["Message"]
        logger.error("A client error occurred: %s", message)
        logger.error("A client error occured: " +
              format(message))
    return response


def run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens):
    """
    Invokes a model with a multimodal prompt.
    Args:
        bedrock_runtime: The Amazon Bedrock boto3 client.
        model_id (str): The model ID to use.
        messages (JSON) : The messages to send to the model.
        max_tokens (int) : The maximum  number of tokens to generate.
    Returns:
        None.
    """
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
             "messages": messages
        }
    )

    response = bedrock_runtime.invoke_model(
        body=body, modelId=model_id)
    response_body = json.loads(response.get('body').read())

    return response_body

def image_to_attributes(image_uri: str,s3_client) -> dict:
    prompt = """Provide the list of all the product attributes for the main product in the image in JSON format"""

    if image_uri.startswith("s3://"):
        im = get_encoded_image_from_uri(image_uri,s3_client)
    else:
        raise ValueError("Invalid S3 URI format, must start with 's3://'")

    responses = content_generation(prompt, im)
    logger.info(json.dumps(responses['content'][0]['text'], indent=4))
    return json.dumps(responses['content'][0]['text'], indent=4)

def image_to_product_description(image_uri: str,s3_client) -> dict:
    prompt = """Write enriched product description for the main product in the image for retailer's product catalog"""

    if image_uri.startswith("s3://"):
        im = get_encoded_image_from_uri(image_uri,s3_client)
    else:
        raise ValueError("Invalid S3 URI format, must start with 's3://'")

    responses = content_generation(prompt, im)
    logger.info(json.dumps(responses['content'][0]['text'], indent=4))
    return json.dumps(responses['content'][0]['text'], indent=4)

def parse_project_attributes_from_dict(attributes_dict: dict) -> dict:
    # Placeholder for actual parsing logic
    return attributes_dict

def parse_list_to_dict(attributes_list: list) -> dict:
    # Placeholder for actual parsing logic
    return {item['name']: item['value'] for item in attributes_list}

# Example usage
# image = "s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg"

# attributes = image_to_attributes(image,)
# logger.info(attributes)

# description = image_to_product_description(image)
# logger.info(description)
