import json
import logging
import pika
from pymongo import MongoClient
import urllib.request
from urllib.error import HTTPError

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

class Spider:
    def __init__(self, message_queue_url, mongodb_url, database_name):
        self.message_queue_url = message_queue_url
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=message_queue_url))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='shopify')
        self.logger = self.setup_logging()

        self.mongo_client = MongoClient(mongodb_url)
        self.db = self.mongo_client[database_name]
        self.collections_collection = self.db['collections']

    def setup_logging(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def isShopify(self, url):
        try:
            req = urllib.request.Request(url + '/collections.json', headers={'User-Agent': USER_AGENT})
            urllib.request.urlopen(req)
            return True
        except:
            return False

    def callback(self, ch, method, properties, body):
        url = body.decode()
        self.logger.info(f"Received URL: {url}")
        if self.isShopify(url):
            self.logger.info(f"Valid URL: {url}")
            self.get_collections(url)
        else:
            self.logger.warning(f"Invalid URL: {url}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='shopify', on_message_callback=self.callback)
        self.channel.start_consuming()

    def get_collections(self, url):
        collections = self.retrieve_collections(url)
        if collections:
            doc = {
                'url': url,
                'collections': collections,
            }
            self.collections_collection.update_one({'url': url}, {'$set': doc}, upsert=True)
            for collection in collections:
                collection_name = collection.get('handle', '')
                if collection_name:
                    self.collections_collection.update_one(
                        {'url': url},
                        {'$addToSet': {'collections': {'$each': [collection]}}},
                    )
                    self.get_products_of_collection(url, collection_name)
        
    def get_products_of_collection(self, url, collection_name):
        products = self.retrieve_products(url, collection_name)
        if products:
            self.collections_collection.update_one(
                {'url': url, 'collections.handle': collection_name},
                {'$push': {'collections.$.products': {'$each': products}}},
            )
    

    
        
    

    def retrieve_collections(self, url):
        collections_url = f"{url}/collections.json"
        req = urllib.request.Request(collections_url, headers={'User-Agent': USER_AGENT})
        try:
            response = urllib.request.urlopen(req)
            response_data = response.read().decode('utf-8')
            if response_data:
                collections_data = json.loads(response_data)
                collections = collections_data.get('collections', [])
                return collections
            else:
                self.logger.warning(f"Empty response while retrieving collections from URL: {url}")
                return []
        except HTTPError as e:
            self.logger.error(f"Error retrieving collections: {e}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON response while retrieving collections from URL: {url}: {e}")
            return []

    def retrieve_products(self, url, collection_name):
        products_url = f"{url}/collections/{collection_name}/products.json"
        req = urllib.request.Request(products_url, headers={'User-Agent': USER_AGENT})
        try:
            response = urllib.request.urlopen(req)
            response_data = response.read().decode('utf-8')
            if response_data:
                products_data = json.loads(response_data)
                products = products_data.get('products', [])
                return products
            else:
                self.logger.warning(f"Empty response while retrieving products from URL: {url}, collection name: {collection_name}")
                return []
        except HTTPError as e:
            self.logger.error(f"Error retrieving products: {e}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON response while retrieving products from URL: {url}, collection name: {collection_name}: {e}")
            return []

if __name__ == '__main__':
    message_queue_url = 'localhost'  # Replace with the actual message queue URL
    mongodb_url = 'mongodb://localhost:27017/'  # Replace with the actual MongoDB URL
    database_name = 'shopify'  # Replace with the name of your MongoDB database

    spider = Spider(message_queue_url, mongodb_url, database_name)
    spider.start_consuming()
