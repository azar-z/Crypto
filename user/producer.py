import json

import environ
import pika

env = environ.Env()
environ.Env.read_env()

SMS_PROVIDER_USERNAME = env('SMS_PROVIDER_USERNAME')
SMS_PROVIDER_PASSWORD = env('SMS_PROVIDER_PASSWORD')
SMS_PRIVATE_NUMBER = env('SMS_PRIVATE_NUMBER')

params = pika.URLParameters('amqps://smzjfcgh:A7V6MO-h8Z7IrW7gqolJxkHixvXMciVQ@sparrow.rmq.cloudamqp.com/smzjfcgh')

connection = pika.BlockingConnection(params)

channel = connection.channel()


def publish(method, data):
    data.update({
        'username': SMS_PROVIDER_USERNAME,
        'password': SMS_PROVIDER_PASSWORD,
        'private_number': SMS_PRIVATE_NUMBER,
    })
    properties = pika.BasicProperties(method)
    body = json.dumps(data).encode('utf-8')
    channel.basic_publish(exchange='', routing_key='SMSMicroservice', body=body, properties=properties)
    print('published')
