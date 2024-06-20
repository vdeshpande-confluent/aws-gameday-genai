import os
import logging
import boto3
from kaggle.api.kaggle_api_extended import KaggleApi
import sys
logger = logging.getLogger(__name__)

# Initialize Kaggle API
kaggle_api = KaggleApi()
kaggle_api.authenticate()

s3_client = boto3.client('s3')

def download_and_upload(dataset_name,s3_bucket,context_data_size):
    # Download dataset
    context_data_size = int(context_data_size)
    logger.info(f"Downloading dataset: {dataset_name}")
    kaggle_api.dataset_download_files(dataset_name, path='/tmp', unzip=True)
    
    # Upload to S3 bucket
    base_path = '/tmp/Khaadi_Data'
    logger.info("Uploading the dataset to S3 bucket")
    count = 0
    exit_loops = False

    for root, _, files in os.walk(base_path):
        if exit_loops:
            break
        for file in files:
            if count >= context_data_size:
                exit_loops = True
                break
            logger.info(f"Uploading file: {file}")
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, base_path)
            s3_key = f'raw-dataset/{relative_path}'
            s3_client.upload_file(local_path, s3_bucket, s3_key)
            count += 1


def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <arg1> <arg2>")
        return
    
    dataset_name = 'usman8/khaadis-clothes-data-with-images'
    s3_bucket = sys.argv[1]
    context_data_size = sys.argv[2]

    print(f"Argument 1: {s3_bucket}")
    print(f"Argument 2: {context_data_size}")
    
    download_and_upload(dataset_name, s3_bucket, context_data_size)
    
    

if __name__ == "__main__":
    main()


