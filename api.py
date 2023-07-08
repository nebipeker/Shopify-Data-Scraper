import logging
from flask import Flask, request, jsonify
from spider import Spider

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Spider instance for handling requests
spider = Spider()

# Route for retrieving collection handles
@app.route("/shopify/collections")
def get_collections():
    url = request.args.get('site')
    if url:
        logging.info(f"Retrieving collection handles for URL: {url}")
        if spider.isShopify(url):
            spider.get_collections(url)
            return "Retrieving collection handles. Please check the logs for progress."
        else:
            logging.warning(f"Invalid URL: {url}")
            return "Invalid URL provided."
    else:
        logging.warning("No URL provided")
        return "No URL provided."

# Route for retrieving products of a collection
@app.route("/shopify/collections/<collection>/products")
def get_products(collection):
    url = request.args.get('site')
    if url:
        logging.info(f"Retrieving products for URL: {url}, collection: {collection}")
        if spider.isShopify(url):
            spider.get_products_of_collection(url, collection)
            return "Retrieving products. Please check the logs for progress."
        else:
            logging.warning(f"Invalid URL: {url}")
            return "Invalid URL provided."
    else:
        logging.warning("No URL provided")
        return "No URL provided."

if __name__ == "__main__":
    app.run()
