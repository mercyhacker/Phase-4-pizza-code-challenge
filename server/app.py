#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants")
def restaurant():
    restaurants = Restaurant.query.all()
    restaurants_list = []

    for each_restaurant in restaurants:
        restaurant_dict = {
            "address": each_restaurant.address,
            "id": each_restaurant.id,
            "name": each_restaurant.name
        }
        restaurants_list.append(restaurant_dict)
    response = make_response(jsonify(restaurants_list), 200)
    return response

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    each_restaurant = Restaurant.query.get(id)
    if each_restaurant:
        # Create a list of associated restaurant_pizzas
        restaurant_pizzas = [{
            "id": rp.id,
            "price": rp.price,
            "pizza_id": rp.pizza_id
        } for rp in each_restaurant.Restaurant_Pizza]  # Assuming this is the relationship name

        restaurants_dict = {
            "id": each_restaurant.id,
            "name": each_restaurant.name,
            "address": each_restaurant.address,
            "restaurant_pizzas": restaurant_pizzas  # Include restaurant_pizzas
        }
        response = make_response(jsonify(restaurants_dict))
        return response
    else:
        response = make_response(jsonify({"error": "Restaurant not found"}), 404)
        return response

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)
    else:
        response = {"error": "Restaurant not found"}
        return make_response(jsonify(response), 404)

@app.route("/pizzas", methods=["GET"])
def pizza():
    pizzas = Pizza.query.all()
    pizza_list = []
    for each_pizza in pizzas:
        pizza_dict = {
            "id": each_pizza.id,
            "name": each_pizza.name,
            "ingredients": each_pizza.ingredients
        }
        pizza_list.append(pizza_dict)
    response = make_response(jsonify(pizza_list), 200)
    return response

@app.route("/restaurant_pizzas", methods=["POST"])
@app.route("/restaurant_pizzas", methods=["POST"])
def add_pizza():
    data = request.get_json()

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get('restaurant_id')

    # Validate input parameters
    if not all([price is not None, pizza_id is not None, restaurant_id is not None]):
        return jsonify({"errors": ["Missing parameter"]}), 400

    # Validate price range
    if price is None or price < 1 or price > 30:
        return jsonify({"errors": ["validation errors"]}), 400

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        return jsonify({"error": "Invalid pizza id or restaurant id"}), 404

    new_restaurant_pizza = RestaurantPizza(
        price=price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )

    db.session.add(new_restaurant_pizza)
    db.session.commit()

    # Get the new restaurant pizza data to return in the response
    response_data = {
        "id": new_restaurant_pizza.id,
        "price": new_restaurant_pizza.price,
        "pizza_id": new_restaurant_pizza.pizza_id,
        "restaurant_id": new_restaurant_pizza.restaurant_id,
        "pizza": {"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients},
        "restaurant": {"id": restaurant.id}  # Add any restaurant details if needed
    }

    return make_response(jsonify(response_data), 201)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
