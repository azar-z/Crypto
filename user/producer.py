import json

import pika

params = pika.URLParameters('amqps://smzjfcgh:A7V6MO-h8Z7IrW7gqolJxkHixvXMciVQ@sparrow.rmq.cloudamqp.com/smzjfcgh')

connection = pika.BlockingConnection(params)

channel = connection.channel()


def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='sms', body=json.dumps(body).encode('utf-8'), properties=properties)
