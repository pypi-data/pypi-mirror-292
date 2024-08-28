import json
from confluent_kafka import Producer


def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print('Event sent successfully.')

def send_event(topic, payloadPath, config):
    producer = Producer(config)
    topic = topic
    file_data = open(payloadPath)
    data = json.load(file_data)
    file_data.close()
    json_str = json.dumps(data)
    bytes_obj = bytes(json_str, 'utf-8')
    producer.produce(topic, value = bytes_obj, callback=delivery_callback)
    
    # Block until the messages are sent.
    producer.poll()
