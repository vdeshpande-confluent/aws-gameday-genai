import logging
logger = logging.getLogger()
logger.setLevel("INFO")

def list_images_in_bucket(bucket_name, folder_name,s3_client,context_size):
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=folder_name)
    image_list = []
    for page in pages:
        if len(image_list) > context_size:
            break
        for obj in page.get('Contents', []):
            image_list.append(f"s3://{bucket_name}/{obj['Key']}")
    logging.info(f"{len(image_list)} Images retrieved from s3")
    return image_list