from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import os 
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)
class Context(object):
    def __init__(self, ProductImageIndexID, ProductDescription, ProductId, ProductImageGCSUri,ProductAttributes,ProductTextIndexID):
        self.ProductImageIndexID = ProductImageIndexID
        self.ProductDescription = ProductDescription
        self.ProductId = ProductId
        self.ProductImageGCSUri = ProductImageGCSUri
        self.ProductAttributes = ProductAttributes
        self.ProductTextIndexID = ProductTextIndexID


def context_to_dict(prompt, ctx):
    return dict(ProductImageIndexID=prompt.ProductImageIndexID,
                ProductDescription=prompt.ProductDescription,
                ProductId=prompt.ProductId,ProductImageGCSUri=prompt.ProductImageGCSUri,ProductAttributes=prompt.ProductAttributes,ProductTextIndexID=prompt.ProductTextIndexID)





def delivery_report(err, msg):
    if err is not None:
        logger.info("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    logger.info(' Record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))


def setup_producer():
    logger.info(f"Setting up producer configurations")
    logger.info(f"Schema registry url{os.getenv('schema.registry.url')}")
    logger.info(f"Schema registry config {os.getenv('schema.registry.basic.auth.user.info')}")
    sr = SchemaRegistryClient( {
            'url':os.getenv('schema.registry.url'),
    'basic.auth.user.info': os.getenv('schema.registry.basic.auth.user.info')
    })
    logger.info(f"bootstrap.servers {os.getenv('bootstrap.servers')}")
    logger.info(f"sasl.username {os.getenv('sasl.username')}")
    logger.info(f"sasl.password {os.getenv('sasl.password')}")
    producer_conf = {
        'bootstrap.servers':  os.getenv('bootstrap.servers'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms':'PLAIN',
        'sasl.username': os.getenv('sasl.username'),
        'sasl.password':os.getenv('sasl.password')
    }
    topic = os.getenv('context_topic_name')
    logger.info(f"topic {topic}")
    producer = Producer(producer_conf)
    return topic,producer,sr

def run_producer(topic,producer,sr,key,message):
    logger.info(f"Reading and serliazing schema string")
    with open("avro/context.avsc") as f:
        schema_str = f.read()
    
    avro_serializer = AvroSerializer(sr,
                                     schema_str,
                                     context_to_dict)
    

    path = os.path.realpath(os.path.dirname(__file__))
    logger.info(f"Producing message to kafka topic")
    logger.info(f"Key {key} , value ={message}")
    producer.produce(topic=topic,key=key,
                             value=avro_serializer(message, SerializationContext(topic, MessageField.VALUE)),on_delivery=delivery_report)
    logger.info(f"Record {key} produced successfully")