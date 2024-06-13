import random
import json
import os
import argparse
from faker import Faker
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

fake = Faker()

class Product(object):
    def __init__(self, product_id, description, image_uri, attributes, image_index_id, text_index_id):
        self.product_id = product_id
        self.description = description
        self.image_uri = image_uri
        self.attributes = attributes
        self.image_index_id = image_index_id
        self.text_index_id = text_index_id

def product_to_dict(product, ctx):
    return product
    # return {
    #     "ProductId": product.product_id,
    #     "ProductDescription": product.description,
    #     "ProductImageGCSUri": product.image_uri,
    #     "ProductAttributes": product.attributes,
    #     "ProductImageIndexID": product.image_index_id,
    #     "ProductTextIndexID": product.text_index_id
    # }

def read_ccloud_config(config_file):
    omitted_fields = set([])
    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                if parameter not in omitted_fields:
                    conf[parameter] = value.strip()
    return conf

def generate_mock_product(product_id):
    description = fake.sentence()
    image_uri = fake.image_url()
    attributes = fake.word()
    image_index_id = f"{product_id}_image"
    text_index_id = f"{product_id}_text"
    
    product = Product(
        product_id=product_id,
        description=description,
        image_uri=image_uri,
        attributes=attributes,
        image_index_id=image_index_id,
        text_index_id=text_index_id
    )
    
    return product

def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed for Product record {}: {}".format(msg.key(), err))
        return
    print('Product record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

def run_producer(products, conf, producer):
    for product in products:
        produce_search_results(product, conf['context_topic_name'], producer)
    return "Matched results published successfully"

def produce_search_results(message, topic, producer):
    producer.produce(topic=topic,
                     value=avro_serializer(message, SerializationContext(topic, MessageField.VALUE)),
                     on_delivery=delivery_report)
    producer.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate JSON object based on Avro schema")
    
    # Generate mock products with ProductId between 400 and 450 sequentially
    products = [generate_mock_product(product_id) for product_id in range(500, 580)]
    product_attributes = "{\"product_attributes\": [{\"attribute_name\": \"Color\", \"attribute_value\": \"Blue\"}, {\"attribute_name\": \"Size\", \"attribute_value\": \"Medium\"}, {\"attribute_name\": \"Material\", \"attribute_value\": \"Cotton\"}, {\"attribute_name\": \"Pattern\", \"attribute_value\": \"Anarkali\"}]}"  
    product_image_uri = "s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg"
    product_id = 1103
    product = {'ProductId': product_id,'ProductImageIndexID':f'{product_id}_image','ProductTextIndexID':f'{product_id}_text', 'ProductDescription':'This a blue women anarkali dress','ProductImageGCSUri':product_image_uri , 'ProductAttributes':product_attributes }

    products = [product]
    conf = read_ccloud_config("client.properties")
    sr = SchemaRegistryClient({
        'url': conf['schema.registry.url'],
        'basic.auth.user.info': conf['schema.registry.basic.auth.user.info']
    })

    path = os.path.realpath(os.path.dirname(__file__))
    with open(f"{path}/avro/context.avsc") as f:
        schema_str = f.read()
    avro_serializer = AvroSerializer(sr,
                                     schema_str,
                                     product_to_dict)

    producer_conf = {
        'bootstrap.servers': conf['bootstrap.servers'],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': conf['sasl.username'],
        'sasl.password': conf['sasl.password']
    }

    producer = Producer(producer_conf)

    run_producer(products, conf, producer)
    print("Mock data generated and produced.")
