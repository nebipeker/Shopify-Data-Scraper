import json
import time
import urllib.request
from urllib.error import HTTPError
import logging
import pika

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

class Spider:
    def __init__(self, message_queue_url):
        self.message_queue_url = message_queue_url
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=message_queue_url))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='spider_queue')
        self.logger = self.setup_logging()

    def setup_logging(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def get_collections(self, url):
        # Same implementation as before, but modify it to send messages to the message queue instead of returning collections directly
        collections_url = url + 'collections.json'
        page = 1
        while True:
            # ...
            # Instead of returning collections, send messages to the message queue
            self.channel.basic_publish(
                exchange='',
                routing_key='spider_queue',
                body=json.dumps({
                    'url': url,
                    'collection_page': page
                })
            )
            # ...

    def get_products_of_collection(self, url, collection):
        # Same implementation as before, but modify it to send messages to the message queue instead of returning products directly
        page = 1
        while True:
            # ...
            # Instead of returning products, send messages to the message queue
            self.channel.basic_publish(
                exchange='',
                routing_key='spider_queue',
                body=json.dumps({
                    'url': url,
                    'collection': collection,
                    'product_page': page
                })
            )
            # ...

    def isShopify(self, url):
        # Same implementation as before, but modify it to return a boolean indicating if the URL is valid
        try:
            self.get_collections(url)  # Modify this to use the new method for sending messages
            return True
        except:
            return False

    def callback(self, ch, method, properties, body):
        task = json.loads(body)
        url = task['url']
        if 'collection_page' in task:
            collection_page = task['collection_page']
            self.logger.info(f"Retrieving collections for URL: {url}, page: {collection_page}")
            if self.isShopify(url):
                collections = self.retrieve_collections(url, collection_page)
                self.logger.info(f"Retrieved collections for URL: {url}, page: {collection_page}")
                for collection in collections:
                    self.get_products_of_collection(url, collection)
            else:
                self.logger.warning(f"Invalid URL: {url}")
        elif 'product_page' in task:
            collection = task['collection']
            product_page = task['product_page']
            self.logger.info(f"Retrieving products for URL: {url}, collection: {collection}, page: {product_page}")
            if self.isShopify(url):
                products = self.retrieve_products(url, collection, product_page)
                self.logger.info(f"Retrieved products for URL: {url}, collection: {collection}, page: {product_page}")
            else:
                self.logger.warning(f"Invalid URL: {url}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='spider_queue', on_message_callback=self.callback)
        self.channel.start_consuming()

    def retrieve_collections(self, url, page):
        # Modify this method to retrieve collections from the Shopify API based on the given URL and page
        # Return the collections instead of sending messages to the message queue
        pass
    def retrieve_products(self, url, collection, page):
        # Modify this method to retrieve products from the Shopify API based on the given URL, collection, and page
        # Return the products instead of sending messages to the message queue
        pass


if __name__ == '__main__':
    message_queue_url = 'localhost'  # Replace with the actual message queue URL
    spider = Spider(message_queue_url)
    spider.start_consuming()
