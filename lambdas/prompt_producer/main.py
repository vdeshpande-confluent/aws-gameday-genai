from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from run_producer import setup_producer,run_producer
from model import Prompt
import os 
import logging
logger = logging.getLogger()
logger.setLevel("INFO")

topic,producer,sr=setup_producer()

def lambda_handler(event,context):
    prompt_id = event['prompt_id']
    prompt_text = event['prompt_text']
    image_uri = event['image_uri']
    prompt_obj = Prompt(prompt_id=prompt_id,text= prompt_text,image_url=image_uri,session_id=1)
    run_producer(prompt_obj,sr,producer,topic)
    
# event = [{'payload':{'prompt_text':'','image_uri':''}}]
# lambda_handler(event,context='context')

