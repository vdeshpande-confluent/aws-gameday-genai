import json
import os
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import logging
logger = logging.getLogger()
logger.setLevel("INFO")

def prompt_to_dict(prompt, ctx):
    return prompt

def delivery_report(err, msg):
    if err is not None:
        logger.error("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    logger.info('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

def run_producer(matched_items,prompt_details,producer_conf,schema_conf,kafka_topic_name):
    prompt_matched_responses= {
        'prompt_details':prompt_details,
        'matched_indexes' : matched_items
    }
    logger.info(prompt_matched_responses['prompt_details'])
    sr = SchemaRegistryClient({
        'url': schema_conf['url'],
        'basic.auth.user.info': schema_conf['basic.auth.user.info']
    })

    path = os.path.realpath(os.path.dirname(__file__))
    with open(f"{path}/avro/prompt_embedding.avsc") as f:
        schema_str = f.read()
    avro_serializer = AvroSerializer(sr,
                                     schema_str,
                                     prompt_to_dict)


    producer_conf = {
        'bootstrap.servers': producer_conf['bootstrap.servers'],
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms':'PLAIN',
        'sasl.username': producer_conf['sasl.username'],
        'sasl.password':producer_conf['sasl.password']
    }
    logger.info('producer initialize')
    producer = Producer(producer_conf)
    producer.produce(topic=kafka_topic_name,
                     value=avro_serializer(prompt_matched_responses, SerializationContext(kafka_topic_name, MessageField.VALUE)),
                     on_delivery=delivery_report)
                     
    producer.flush()
    return "Matched results published successfully"
