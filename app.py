import json
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
import statistics

import claude

app = Flask(__name__)
CORS(app)

products = []
links = []


def process_link(new_link, all_links):

    all_links_stringified = ", ".join(all_links)


    # list[dict]
    all_products_gotten = claude.get_product_details_csv(all_links_stringified)






    # This is a placeholder function. You'll need to implement the actual logic.
    # For now, it returns dummy data for all products.
    all_products_out = []

    # content_body is a list
    content_string = all_products_gotten['content'][0]['text']

    all_products_loaded = json.loads(content_string)

    for product_dict in all_products_loaded:

        all_products_out.append({
            "product_name": product_dict["product_name"],
            "sustainability_index": product_dict["index"],
        })


    return all_products_out


def calculate_percentages(products):
    if len(products) <= 1:
        return products

    indices = [p['sustainability_index'] for p in products]
    median = statistics.median(indices)

    for product in products:
        index = product['sustainability_index']
        product['percentage'] = (index / median - 1) * 100

    return products


@app.route('/add_product', methods=['POST'])
def add_product():
    new_link = request.json['link']
    links.append(new_link)

    # Process all links, including the new one
    products = process_link(new_link, links)

    # Calculate percentages
    updated_products = calculate_percentages(products)

    return jsonify(updated_products)


@app.route('/get_products', methods=['GET'])
def get_products():
    return jsonify(products)


@app.route('/reset', methods=['POST'])
def reset():
    global products, links
    products = []
    links = []
    return jsonify({"message": "Reset successful"})


if __name__ == '__main__':
    app.run(debug=True)