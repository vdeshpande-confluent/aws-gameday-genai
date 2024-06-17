#!/bin/bash

# Function to check if aws cli is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null
    then
        echo "aws cli not found. Please install AWS CLI and configure it."
        exit 1
    fi
}




# Function to zip the folder
zip_folder() {
    local folder_path="lambdas/"$2
    local zip_file_name=$2

    if [ -d "$folder_path" ]; then
        zip -r "$zip_file_name" "$folder_path"
        echo "Folder zipped successfully: $zip_file_name".zip" "
    else
        echo "Folder not found: $folder_path"
        exit 1
    fi
}

# Function to upload the zip file to S3
upload_to_s3() {
    local zip_file_name=$1".zip"
    local s3_bucket=$2

    if aws s3 cp "$zip_file_name" "s3://$s3_bucket/"; then
        echo "File uploaded successfully to S3: s3://$s3_bucket/$zip_file_name"
    else
        echo "Failed to upload file to S3"
        exit 1
    fi
}

# Main script execution
main() {
    local folder_path="/"
    local s3_bucket="gameday-cflt-code"

    if [ -z "$folder_path" ] || [ -z "$s3_bucket" ]; then
        echo "Usage: $0 <folder_path> <s3_bucket>"
        exit 1
    fi

    check_aws_cli

    local zip_file_context="context_client"
    local zip_file_prompt="prompt_client"
    local zip_file_data="data_generation_client"
    local zip_file_result="synthesize_result_client"
    local zip_file_sdk_layer="awsgameday_confluent_sdk_v2"
    
    zip_folder "$folder_path" "$zip_file_context"
    upload_to_s3 "$zip_file_context" "$s3_bucket"

    zip_folder "$folder_path" "$zip_file_prompt"
    upload_to_s3 "$zip_file_prompt" "$s3_bucket"

    zip_folder "$folder_path" "$zip_file_data"
    upload_to_s3 "$zip_file_data" "$s3_bucket"

    zip_folder "$folder_path" "$zip_file_result"
    upload_to_s3 "$zip_file_result" "$s3_bucket"

    upload_to_s3 "$zip_file_sdk_layer" "$s3_bucket"
}

# Run the main function with all script arguments
main "$@"
