import logging

logger = logging.getLogger(__name__)

def list_images_in_bucket(bucket_name, folder_name,s3_client):
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=folder_name)

    image_list = []
    for page in pages:
        for obj in page.get('Contents', []):
            image_list.append(f"s3://{bucket_name}/{obj['Key']}")

    return image_list