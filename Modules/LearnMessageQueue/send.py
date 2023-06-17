import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange_type='topic', exchange='hello_exchange', durable=True)

channel.queue_declare(queue='hello', durable=True)

channel.basic_publish(exchange='hello_exchange', routing_key='hello', body='Hello World!')
print(" [x] Sent 'Hello World!'")

connection.close()