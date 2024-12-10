from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from http import HTTPStatus

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "vehicle_rental_db"

mysql = MySQL(app)

@app.route("/")
def hello_world():
    
    style = """
        <style>
            p {
                font-family: Arial, sans-serif;
                font-size: 50px;
                color: blue;
                text-align: center;
            }
        </style>
    """
    return f"{style} <p>VEHICLE RENTAL SYSTEM MANAGEMENT</p>"

# READ CUSTOMERS
@app.route("/customers", methods=["GET"])
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

# UPDATE CUSTOMERS
@app.route("/customers/<int:customer_id>", methods=["PUT"])
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

# DELETE CUSTOMERS
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Customers WHERE customer_id = %s", (customer_id,))
        mysql.connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify({"message": "Customer deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)