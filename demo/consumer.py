from confluent_kafka import Consumer
import time
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.avro import AvroDeserializer
import os
import json
def read_ccloud_config(config_file):
    omitted_fields = set(['schema.registry.url', 'basic.auth.credentials.source', 'basic.auth.user.info'])
    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                if parameter not in omitted_fields:
                    conf[parameter] = value.strip()
    return conf

def consume():
    conf = read_ccloud_config("client.properties")
    consumer = Consumer({'bootstrap.servers': conf['bootstrap.servers'], 'group.id': conf['group.id'], 'session.timeout.ms': 6000,
            'auto.offset.reset': conf['auto.offset.reset'], 'enable.auto.offset.store': False,
            'security.protocol': 'SASL_SSL',
        'sasl.mechanisms':'PLAIN',
        'sasl.username': conf['sasl.username'],
        'sasl.password':conf['sasl.password']})
    consumer.subscribe(['success-lcc-56wdpg'])
    mem_db = []
    while True:
        
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg is not None:
                data = json.loads(json.loads(msg.value()))
                if data.get("prompt_id") not in mem_db:
                    print(data.get("generatedAnswer"))
                    mem_db.append(data.get("prompt_id"))
        except KeyboardInterrupt:
            break

    consumer.close()
consume()