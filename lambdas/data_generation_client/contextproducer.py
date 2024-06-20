from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import os 
import logging
logger = logging.getLogger()
logger.setLevel("INFO")


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
        logger.error("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    logger.info(' Record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))


def setup_producer():
    logger.info(f"Setting up producer configurations")
    logger.info(f"Schema registry url{os.getenv('SR_URL')}")
    # logger.info(f"Schema registry config {os.getenv('schema.registry.basic.auth.user.info')}")
    sr = SchemaRegistryClient( {
            'url':os.getenv('SR_URL'),
    'basic.auth.user.info': f"{os.getenv('SR_API_KEY')}:{os.getenv('SR_API_SECRET')}"
    })
    logger.info(f"bootstrap.servers {os.getenv('BOOTSTRAP_KAFKA_SERVER')}")
    logger.info(f"sasl.username {os.getenv('KAFKA_API_KEY')}")
    logger.info(f"sasl.password {os.getenv('KAFKA_API_SECRET')}")
    producer_conf = {
        'bootstrap.servers':  os.getenv('BOOTSTRAP_KAFKA_SERVER'),
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms':'PLAIN',
        'sasl.username': os.getenv('KAFKA_API_KEY'),
        'sasl.password':os.getenv('KAFKA_API_SECRET')
    }
    topic = os.getenv('KAFKA_TOPIC_NAME')
    logger.info(f"topic {topic}")
    producer = Producer(producer_conf)
    return topic,producer,sr

def run_producer(topic,producer,sr,key,message):
    logger.info(f"Reading and serliazing schema string")
    path = os.path.realpath(os.path.dirname(__file__))
    with open(f"{path}/avro/context.avsc") as f:
        schema_str = f.read()
    logger.info(f"Read")
    avro_serializer = AvroSerializer(sr,
                                     schema_str,
                                     context_to_dict)
    

    logger.info(f"Producing message to kafka topic")
    logger.info(f"Key {key} , value ={message}")
    producer.produce(topic=topic,key=key,
                             value=avro_serializer(message, SerializationContext(topic, MessageField.VALUE)),on_delivery=delivery_report)
    logger.info(f"Record {key} produced successfully")