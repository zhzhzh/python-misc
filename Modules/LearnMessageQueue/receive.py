import os

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

channel.queue_declare(queue="hello")


def callback(ch, method, properties, body):
    print(f" [x] Received {body} from {os.getpid()}")


channel.basic_consume("hello", callback, auto_ack=True)

print(" [*] Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
