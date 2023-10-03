# Shopify Data Scraper

This repository contains a Python application for scraping data from Shopify websites and storing it in a MongoDB database. It consists of the following components:

- `spider.py`: The main spider script responsible for scraping Shopify data.
- `api.py`: A Flask API for interacting with the spider and initiating data scraping.
- `Dockerfile`: Docker configuration for containerizing the application.
- `docker-compose.yml`: Docker Compose configuration for running the application with MongoDB.

## Prerequisites

Before running the application, make sure you have the following prerequisites installed:

- Docker: To containerize and run the application.
- Python 3.9 or higher: Required for the spider and Flask API.

## Getting Started

1. Clone this repository to your local machine.

```bash
git clone https://github.com/nebipeker/shopify-scraper.git
cd shopify-scraper
```

2. Modify the `message_queue_url` and `mongodb_url` in `spider.py` to match your environment settings.

3. Build and start the Docker containers using Docker Compose:

```bash
docker-compose up --build
```

This will start the Flask API and MongoDB containers.

4. Access the API at `http://localhost:5000` to interact with the spider for data scraping. Use the following endpoints:

- `/shopify/collections`: Retrieve collection handles for a given Shopify site.
- `/shopify/collections/<collection>/products`: Retrieve products of a specific collection on a Shopify site.

## Usage

To use the API, make HTTP requests to the specified endpoints, providing the necessary parameters. Refer to the API.py code for details on the available endpoints and their usage.

## Logging

Application logs are stored in the `app.log` file, which captures information, warnings, and errors related to the scraping process.

## Cleanup

To stop and remove the Docker containers, run:

```bash
docker-compose down
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


