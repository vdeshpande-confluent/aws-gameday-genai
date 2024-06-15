# HumanRequest class
class HumanRequest:
    def __init__(self, prompt_text, product_description, product_attributes, product_gcs_uri, prompt_image_url):
        self.prompt_text = prompt_text
        self.product_description = product_description
        self.product_attributes = product_attributes
        self.product_gcs_uri = product_gcs_uri
        self.prompt_image_url = prompt_image_url