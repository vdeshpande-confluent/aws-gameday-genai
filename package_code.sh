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
    local folder_path="lambdas/$2"
    local zip_file_name="$2.zip"

    if [ -d "$folder_path" ]; then
        # Change to the folder directory
        cd "$folder_path" || exit 1

        # Zip the contents of the folder (not the folder itself)
        zip -r "../$zip_file_name" .

        # Move back to the original directory
        cd - > /dev/null || exit 1

        echo "Folder contents zipped successfully: $zip_file_name"
    else
        echo "Folder not found: $folder_path"
        exit 1
    fi
}

# Function to upload the zip file to S3
upload_to_s3() {
    local zip_file_name="lambdas/"$1".zip"
    local s3_bucket=$2

    if aws s3 cp "$zip_file_name" "s3://$s3_bucket/"; then
        echo "File uploaded successfully to S3: s3://$s3_bucket/$zip_file_name"
    else
        echo "Failed to upload file to S3"
        exit 1
    fi
}

generate_upload_data(){
    PYTHON_DATA_SCRIPT="upload_dataset.py"

    # Check if the Upload Data Python script exists
    if [ -f "$PYTHON_DATA_SCRIPT" ]; then
         # Replace with your actual S3 bucket name
        ARG1=$1
        ARG2=10
        
        # Run the Python script with arguments
        python3 "$PYTHON_DATA_SCRIPT" "$ARG1" "$ARG2"
        
        # Check the exit status of the Python script
        if [ $? -eq 0 ]; then
            echo "Python script executed successfully."
        else
            echo "Python script failed to execute."
        fi
    else
        echo "Python script not found: $PYTHON_DATA_SCRIPT"
    fi


}
# Main script execution
main() {
    local folder_path="/"
    local s3_bucket="cflt-gameday-code"
    local s3_data_bucket="cflt-gameday-data"

    if [ -z "$folder_path" ] || [ -z "$s3_bucket" ]; then
        echo "Usage: $0 <folder_path> <s3_bucket>"
        exit 1
    fi

    check_aws_cli

    # generate_upload_data "$s3_data_bucket"

    local zip_file_context="context_client"
    local zip_file_prompt="prompt_client"
    local zip_file_data="data_generation_client"
    local zip_file_result="synthesize_result_client"
    local zip_file_producer="prompt_producer"
    local zip_file_sdk_layer="awsgameday_confluent_sdk_v2"
    
    zip_folder "$folder_path" "$zip_file_context"
    upload_to_s3 "$zip_file_context" "$s3_bucket"

    zip_folder "$folder_path" "$zip_file_prompt"
    upload_to_s3 "$zip_file_prompt" "$s3_bucket"

    zip_folder "$folder_path" "$zip_file_data"
    upload_to_s3 "$zip_file_data" "$s3_bucket"

    zip_folder "$folder_path" "$zip_file_result"
    upload_to_s3 "$zip_file_result" "$s3_bucket"

    zip_folder "$folder_path" "$zip_file_producer"
    upload_to_s3 "$zip_file_producer" "$s3_bucket"

    upload_to_s3 "$zip_file_sdk_layer" "$s3_bucket"

    

}

# Run the main function with all script arguments
main "$@"
