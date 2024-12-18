from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_httpauth import HTTPBasicAuth
import jwt
import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "vehicle_rental_db"
app.config["SECRET_KEY"] = "kyle123"

mysql = MySQL(app)
auth = HTTPBasicAuth()

USER_DATA_FILE = "users.json"

def load_users():
    try:
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file)

users = load_users()

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users[username]['password'], password):
        return username

# Generate JWT
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username not in users or not check_password_hash(users[username]['password'], password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Check if token already exists for the user
    if 'token' not in users[username]:
        token = jwt.encode({
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config["SECRET_KEY"], algorithm="HS256")
        users[username]['token'] = token
        save_users(users)
    else:
        token = users[username]['token']

    return jsonify({"token": token})

# Register a new user
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")  # Default role is "user"

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if username in users:
        return jsonify({"error": "User already exists"}), 400

    users[username] = {
        "password": generate_password_hash(password),
        "role": role
    }
    save_users(users)

    return jsonify({"message": "User registered successfully"}), 201

# JWT Token validation
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            decoded_token = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            request.username = decoded_token["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return wrapper

# Role-based access control
def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            username = getattr(request, "username", None)
            user_role = users.get(username, {}).get("role")
            if not user_role or user_role not in required_roles:
                return jsonify({"error": "Access forbidden: insufficient permissions"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/")
def hello_world():
    style = """
        <style>
            p {
                font-family: Arial, sans-serif;
                font-size: 20px;
                color: blue;
                text-align: center;
            }
            a {
                font-family: Arial, sans-serif;
                font-size: 20px;
                color: green;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    """
    
    no_token_routes = [
        {"name": "Home", "url": "/"},
        {"name": "View Vehicles", "url": "/vehicles"},
        {"name": "View Locations", "url": "/locations"},
    ]

    no_token_links = "".join([f'<p><a href="{route["url"]}">{route["name"]}</a></p>' for route in no_token_routes])
    
    return f"""
        {style}
        <p>VEHICLE RENTAL SYSTEM MANAGEMENT</p>
        {no_token_links}
    """


# READ CUSTOMERS
@app.route("/customers", methods=["GET"])
@token_required
def get_customers():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()

    if not customers:
        return jsonify({"error": "No customers found"}), 404

    customers_list = [
        {
        "customer_id": customer[0], 
        "customer_name": customer[1], 
        "customer_contact": customer[2]
        }
        for customer in customers
    ]

    return jsonify(customers_list), 200

#READ VEHICLES
@app.route("/vehicles", methods=["GET"])
def get_vehicles():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Vehicles")
    vehicles = cursor.fetchall()

    if not vehicles:
        return jsonify({"error": "No vehicles found"}), 404

    vehicles_list = [
        {
            "vehicle_id": vehicle[0],
            "reg_number": vehicle[1],
            "model_name": vehicle[2],
            "daily_hire_rate": vehicle[3],
            "vehicle_type": vehicle[4]
        }
        for vehicle in vehicles
    ]
    
    return jsonify(vehicles_list), 200

#READ LOCATIONS
@app.route("/locations", methods=["GET"])
def get_locations():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Locations")
    locations = cursor.fetchall()

    if not locations:
        return jsonify({"error": "No locations found"}), 404

    locations_list = [
        {
            "location_id": location[0],
            "location_name": location[1],
            "vehicle_id": location[2],
            "is_available": location[3]
        }
        for location in locations
    ]
    
    return jsonify(locations_list), 200

#READ RENTAL
@app.route("/rentals", methods=["GET"])
@token_required
@role_required("staff")
def get_rentals():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Rentals")
    rentals = cursor.fetchall()

    if not rentals:
        return jsonify({"error": "No rentals found"}), 404

    rentals_list = [
        {
            "rental_id": rental[0],
            "customer_id": rental[1],
            "vehicle_id": rental[2],
            "date_from": rental[3],
            "date_to": rental[4],
            "total_cost": rental[5]
        }
        for rental in rentals
    ]
    
    return jsonify(rentals_list), 200

# ADD CUSTOMERS
@app.route("/customers", methods=["POST"])
@token_required
@role_required(["staff", "admin"])
def add_customer():
    data = request.get_json()
    customer_name = data.get("customer_name")
    customer_contact = data.get("customer_contact")

    #VALIDATION
    if not customer_name or not isinstance(customer_name, str):
        return jsonify({"error": "Customer name is required and must be a valid string"}), 400
    if not customer_contact or not isinstance(customer_contact, str):
        return jsonify({"error": "Customer contact is required and must be a valid string"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Customers (customer_name, customer_contact) VALUES (%s, %s)",
            (customer_name, customer_contact),
        )
        mysql.connection.commit()
        return jsonify({"message": "Customer created successfully", "customer_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

#ADD VEHICLES
@app.route("/vehicles", methods=["POST"])
@token_required
@role_required(["staff", "admin"])
def add_vehicle():
    data = request.get_json()
    reg_number = data.get("reg_number")
    model_name = data.get("model_name")
    daily_hire_rate = data.get("daily_hire_rate")
    vehicle_type = data.get("vehicle_type")

    # VALIDATION
    if not reg_number or not isinstance(reg_number, str):
        return jsonify({"error": "Registration number is required and must be a valid string"}), 400
    if not model_name or not isinstance(model_name, str):
        return jsonify({"error": "Model name is required and must be a valid string"}), 400
    if not daily_hire_rate or not isinstance(daily_hire_rate, (int, float)):
        return jsonify({"error": "Daily hire rate is required and must be a valid number"}), 400
    if not vehicle_type or not isinstance(vehicle_type, str):
        return jsonify({"error": "Vehicle type is required and must be a valid string"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Vehicles (reg_number, model_name, daily_hire_rate, vehicle_type) VALUES (%s, %s, %s, %s)",
            (reg_number, model_name, daily_hire_rate, vehicle_type),
        )
        mysql.connection.commit()
        return jsonify({"message": "Vehicle created successfully", "vehicle_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

#ADD LOCATIONS
@app.route("/locations", methods=["POST"])
@token_required
@role_required(["staff", "admin"])
def add_location():
    data = request.get_json()
    location_name = data.get("location_name")
    vehicle_id = data.get("vehicle_id")
    is_available = data.get("is_available")

    # VALIDATION
    if not location_name or not isinstance(location_name, str):
        return jsonify({"error": "Location name is required and must be a valid string"}), 400
    if not vehicle_id or not isinstance(vehicle_id, int):
        return jsonify({"error": "Vehicle ID is required and must be a valid number"}), 400
    if not is_available or not isinstance(is_available, bool):
        return jsonify({"error": "Availability is required and must be a valid boolean"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Locations (location_name, vehicle_id, is_available) VALUES (%s, %s, %s)",
            (location_name, vehicle_id, is_available),
        )
        mysql.connection.commit()
        return jsonify({"message": "Location created successfully", "location_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

#ADD RENTALS
@app.route("/rentals", methods=["POST"])
@token_required
@role_required(["staff", "admin"])
def add_rental():
    data = request.get_json()
    customer_id = data.get("customer_id")
    vehicle_id = data.get("vehicle_id")
    date_from = data.get("date_from")
    date_to = data.get("date_to")
    total_cost = data.get("total_cost")

    # VALIDATION
    if not customer_id or not isinstance(customer_id, int):
        return jsonify({"error": "Customer ID is required and must be a valid number"}), 400
    if not vehicle_id or not isinstance(vehicle_id, int):
        return jsonify({"error": "Vehicle ID is required and must be a valid number"}), 400
    if not date_from or not isinstance(date_from, str):
        return jsonify({"error": "Date from is required and must be a valid string"}), 400
    if not date_to or not isinstance(date_to, str):
        return jsonify({"error": "Date to is required and must be a valid string"}), 400
    if not total_cost or not isinstance(total_cost, (int, float)):
        return jsonify({"error": "Total cost is required and must be a valid number"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO Rentals (customer_id, vehicle_id, date_from, date_to, total_cost) VALUES (%s, %s, %s, %s, %s)",
            (customer_id, vehicle_id, date_from, date_to, total_cost),
        )
        mysql.connection.commit()
        return jsonify({"message": "Rental created successfully", "rental_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

# UPDATE CUSTOMERS
@app.route("/customers/<int:customer_id>", methods=["PUT"])
@token_required
@role_required(["staff", "admin"])
def update_customer(customer_id):
    data = request.get_json()
    customer_name = data.get("customer_name")
    customer_contact = data.get("customer_contact")

    #VALIDATION
    if not customer_name or not isinstance(customer_name, str):
        return jsonify({"error": "Customer name is required and must be a valid string"}), 400
    if not customer_contact or not isinstance(customer_contact, str):
        return jsonify({"error": "Customer contact is required and must be a valid string"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE Customers SET customer_name = %s, customer_contact = %s WHERE customer_id = %s",
            (customer_name, customer_contact, customer_id),
        )
        mysql.connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify({"message": "Customer updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

# UPDATE VEHICLES
@app.route("/vehicles/<int:vehicle_id>", methods=["PUT"])
@token_required
@role_required(["staff", "admin"])
def update_vehicle(vehicle_id):
    data = request.get_json()
    reg_number = data.get("reg_number")
    model_name = data.get("model_name")
    daily_hire_rate = data.get("daily_hire_rate")
    vehicle_type = data.get("vehicle_type")

    # VALIDATION
    if not reg_number or not isinstance(reg_number, str):
        return jsonify({"error": "Registration number is required and must be a valid string"}), 400
    if not model_name or not isinstance(model_name, str):
        return jsonify({"error": "Model name is required and must be a valid string"}), 400
    if not daily_hire_rate or not isinstance(daily_hire_rate, (int, float)):
        return jsonify({"error": "Daily hire rate is required and must be a valid number"}), 400
    if not vehicle_type or not isinstance(vehicle_type, str):
        return jsonify({"error": "Vehicle type is required and must be a valid string"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE Vehicles SET reg_number = %s, model_name = %s, daily_hire_rate = %s, vehicle_type = %s WHERE vehicle_id = %s",
            (reg_number, model_name, daily_hire_rate, vehicle_type, vehicle_id),
        )
        mysql.connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Vehicle not found"}), 404
        return jsonify({"message": "Vehicle updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

# UPDATE LOCATIONS
@app.route("/locations/<int:location_id>", methods=["PUT"])
@token_required
@role_required(["staff", "admin"])
def update_location(location_id):
    data = request.get_json()
    location_name = data.get("location_name")
    vehicle_id = data.get("vehicle_id")
    is_available = data.get("is_available", True)

    # VALIDATION
    if not location_name or not isinstance(location_name, str):
        return jsonify({"error": "Location name is required and must be a valid string"}), 400
    if not vehicle_id or not isinstance(vehicle_id, int):
        return jsonify({"error": "Vehicle ID is required and must be a valid integer"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE Locations SET location_name = %s, vehicle_id = %s, is_available = %s WHERE location_id = %s",
            (location_name, vehicle_id, is_available, location_id),
        )
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Location not found"}), 404

        return jsonify({"message": "Location updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

#UPDATE RENTALS
@app.route("/rentals/<int:rental_id>", methods=["PUT"])
@token_required
@role_required(["staff", "admin"])
def update_rental(rental_id):
    data = request.get_json()
    customer_id = data.get("customer_id")
    vehicle_id = data.get("vehicle_id")
    date_from = data.get("date_from")
    date_to = data.get("date_to")
    total_cost = data.get("total_cost")

    # VALIDATION
    if not customer_id or not isinstance(customer_id, int):
        return jsonify({"error": "Customer ID is required and must be a valid integer"}), 400
    if not vehicle_id or not isinstance(vehicle_id, int):
        return jsonify({"error": "Vehicle ID is required and must be a valid integer"}), 400
    if not date_from or not date_to:
        return jsonify({"error": "Date range is required"}), 400
    if not total_cost or not isinstance(total_cost, (int, float)):
        return jsonify({"error": "Total cost is required and must be a valid number"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE Rentals SET customer_id = %s, vehicle_id = %s, date_from = %s, date_to = %s, total_cost = %s WHERE rental_id = %s",
            (customer_id, vehicle_id, date_from, date_to, total_cost, rental_id),
        )
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Rental not found"}), 404

        return jsonify({"message": "Rental updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500


# DELETE CUSTOMERS
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
@token_required
@role_required(["staff", "admin"])
def delete_customer(customer_id):
    try:
        cursor = mysql.connection.cursor()

        # Set customer_id to NULL in Rentals table where this customer has a rental
        update_rentals_query = "UPDATE Rentals SET customer_id = NULL WHERE customer_id = %s"
        cursor.execute(update_rentals_query, (customer_id,))
        mysql.connection.commit()

        # Delete the customer
        cursor.execute("DELETE FROM Customers WHERE customer_id = %s", (customer_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Customer not found"}), 404

        return jsonify({"message": "Customer deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500


# DELETE VEHICLES
@app.route("/vehicles/<int:vehicle_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete_vehicle(vehicle_id):
    try:
        cursor = mysql.connection.cursor()

        # Set vehicle_id to NULL in Locations table where this vehicle is located
        update_locations_query = "UPDATE Locations SET vehicle_id = NULL WHERE vehicle_id = %s"
        cursor.execute(update_locations_query, (vehicle_id,))
        mysql.connection.commit()

        # Set vehicle_id to NULL in Rentals table where this vehicle is rented
        update_rentals_query = "UPDATE Rentals SET vehicle_id = NULL WHERE vehicle_id = %s"
        cursor.execute(update_rentals_query, (vehicle_id,))
        mysql.connection.commit()

        delete_vehicle_query = "DELETE FROM Vehicles WHERE vehicle_id = %s"
        cursor.execute(delete_vehicle_query, (vehicle_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Vehicle not found"}), 404

        return jsonify({"message": "Vehicle deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# DELETE LOCATIONS
@app.route("/locations/<int:location_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete_location(location_id):
    try:
        cursor = mysql.connection.cursor()

        delete_location_query = "DELETE FROM Locations WHERE location_id = %s"
        cursor.execute(delete_location_query, (location_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Location not found"}), 404

        return jsonify({"message": "Location deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# DELETE RENTALS
@app.route("/rentals/<int:rental_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete_rental(rental_id):
    try:
        cursor = mysql.connection.cursor()

        delete_rental_query = "DELETE FROM Rentals WHERE rental_id = %s"
        cursor.execute(delete_rental_query, (rental_id,))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Rental not found"}), 404

        return jsonify({"message": "Rental deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)