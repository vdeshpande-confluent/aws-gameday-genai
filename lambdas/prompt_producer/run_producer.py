import os
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import logging
logger = logging.getLogger()
logger.setLevel("INFO")
# from dotenv import load_dotenv
# load_dotenv()


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



def prompt_to_dict(prompt, ctx):
    return {
        "prompt_id": prompt.prompt_id,
        "text": prompt.text,
        "image_url": prompt.image_url,
        "session_id": prompt.session_id
    }

def delivery_report(err, msg):
    if err is not None:
        logger.error("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    logger.info('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

def run_producer(prompt, sr, producer,topic):
    logger.info("Starting the producer:")
    path = os.path.realpath(os.path.dirname(__file__))
    with open(f"{path}/avro/prompt.avsc") as f:
        schema_str = f.read()
    avro_serializer = AvroSerializer(sr,
                                     schema_str,
                                     prompt_to_dict)

    producer.produce(topic=topic,
                     value=avro_serializer(prompt, SerializationContext(topic, MessageField.VALUE)),
                     on_delivery=delivery_report)
    producer.flush()
    logger.info("Prompt produced successfully")

    

