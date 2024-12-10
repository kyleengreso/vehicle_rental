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

if __name__ == "__main__":
    app.run(debug=True)