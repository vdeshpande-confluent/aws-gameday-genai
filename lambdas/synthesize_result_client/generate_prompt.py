import base64
import logging
from model import HumanRequest
import logging
logger = logging.getLogger()
logger.setLevel("INFO")

# Function to get encoded image from S3 URI
def get_encoded_image_from_uri(s3_uri,s3_client):
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

# Function to generate prompt
def generate_prompt(humanRequest : HumanRequest,s3_client):
    try:
        # Basic context and user request
        promptContent = (
            f"You are an expert in the clothing market. Your task is to assist the user with the following clothing-related query/request:\n"
            f"Request from User: {humanRequest.prompt_text}"
        )
        
        # Supporting descriptions and attributes
        supportingDescriptions = (
            f"Similar Products Description for Hints (generated from RAG pipeline):\n"
            f"{humanRequest.product_description}"
        )
        supportingAttributes = (
            f"Similar Products Attributes for Hints (generated from RAG pipeline):\n"
            f"{humanRequest.product_attributes}"
        )
        supportingImagePrompt = "Similar Products Images for Hints (generated from RAG pipeline):"
        
        # Handling related images ------------- > Removed because of token limitation
        # relatedImages = list(map(lambda x: get_encoded_image_from_uri(x,s3_client), humanRequest.product_gcs_uri)) 
        
        # Check if there's a reference image provided by the user
        if humanRequest.prompt_image_url:
            prompt_image_text = "\nUser has also provided a reference image/product image to support the task. Image:"
            prompt_image = get_encoded_image_from_uri(humanRequest.prompt_image_url,s3_client)
            
            content = promptContent+ "" +prompt_image_text+ "" +prompt_image+ "" +supportingDescriptions+ "" + supportingAttributes+ "" +supportingImagePrompt
            # content = promptContent+ "" +prompt_image_text+ "" +supportingDescriptions+ "" + supportingAttributes+ "" +supportingImagePrompt
        else:
            content = promptContent+ "" +prompt_image_text+ "" +supportingDescriptions+ "" + supportingAttributes+ "" +supportingImagePrompt
        
        # Add S3 URIs and related images to the content
        for i, uri in enumerate(humanRequest.product_gcs_uri):
            content = content + f"S3 URI for the similar images: {uri}"
            # Handling related images base64 ------------- > Removed because of token limitation
            # content = content + relatedImages[i]+"\n" 
        
        # Add final guidelines
        guidelines = (
            "Following these guidelines is utmost necessary for the product recommendation: \n"
            "1. You have been given two arrays of  as part of the Similar Products Images context, with S3 URIs.\n"
            "2. Return best-matched S3 URIs of the image as a response.\n"
            "3. Your response must be a clothing guide that includes clothing recommendations along with the S3 URI mentioned in point 2."
        )
        content= content +(guidelines)
       
        # logger.info(content)
        logger.info(len(content))
    except Exception as e:
        logger.error(f"Error generating prompt: {e}")
        raise e
    
    return content

