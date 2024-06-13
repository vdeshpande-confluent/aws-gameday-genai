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

class Prompt(object):
    def __init__(self, prompt_id, text, image_url, session_id):
        self.prompt_id = prompt_id
        self.text = text
        self.image_url = image_url
        self.session_id = session_id

def prompt_to_dict(prompt, ctx):
    return {
        "prompt_id": prompt.prompt_id,
        "text": prompt.text,
        "image_url": prompt.image_url,
        "session_id": prompt.session_id
    }

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

def generate_mock_prompt():
    prompt_id = fake.uuid4()
    text = "This is a A-line yellow gown."
    image_url = "s3://awsgameday1/Khaadi_Data/images/ACA231001/image_0.jpg"
    session_id = random.randint(1, 3)
    
    return Prompt(prompt_id, text, image_url, session_id)

def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

def run_producer(prompts, conf, producer):
    for prompt in prompts:
        produce_search_results(prompt, conf['prompt_topic_name'], producer)
    return "Matched results published successfully"

def produce_search_results(message, topic, producer):
    producer.produce(topic=topic,
                     value=avro_serializer(message, SerializationContext(topic, MessageField.VALUE)),
                     on_delivery=delivery_report)
    producer.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate JSON object based on Avro schema")
    
    # Generate 30 mock prompts
    prompts = [generate_mock_prompt() for _ in range(1)]

    conf = read_ccloud_config("client.properties")
    sr = SchemaRegistryClient({
        'url': conf['schema.registry.url'],
        'basic.auth.user.info': conf['schema.registry.basic.auth.user.info']
    })

    path = os.path.realpath(os.path.dirname(__file__))
    with open(f"{path}/avro/prompt.avsc") as f:
        schema_str = f.read()
    avro_serializer = AvroSerializer(sr,
                                     schema_str,
                                     prompt_to_dict)

    producer_conf = {
        'bootstrap.servers': conf['bootstrap.servers'],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'sasl.username': conf['sasl.username'],
        'sasl.password': conf['sasl.password']
    }

    producer = Producer(producer_conf)

    run_producer(prompts, conf, producer)
    print("Mock data generated and produced.")
