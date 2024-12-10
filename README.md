# Vehicle Rental Database API

## Description
A Flask-based REST API for managing customers, vehicles, locations, and rentals in a vehicle rental database.

## Installation
```bash
pip install -r requirements.txt
```

## Configuration
To configure the database:
1. Upload the ```vehicle_rental_db``` MySQL database to your server or local machine.
2. Update the database configuration in the Flask app with your database connection details.

Environment variables needed:
- ```MYSQL_HOST```: The host for the MySQL database (e.g., localhost or IP address of the database server)
- ```MYSQL_USER```: MySQL username (e.g., root)
- ```MYSQL_PASSWORD```: MySQL password
- ```MYSQL_DB```: Name of the database (e.g., vehicle_rental_db)

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /	| GET	| Welcome message |
| /customers	| GET	| List all customers |
| /customers	| POST	| Add a new customer |
| /customers/<customer_id>	| PUT	| Update a customer's details |
| /customers/<customer_id>	| DELETE	| Delete a customer |
| /vehicles	| GET	| List all vehicle |
| /vehicles	| POST	| Add a new vehicle |
| /vehicles/<vehicle_id>	| PUT	| Update a vehicle's details |
| /vehicles/<vehicle_id>	| DELETE	| Delete a vehicle |
| /locations	| GET	| List all location |
| /locations	| POST	| Add a new location |
| /locations/<location_id>	| PUT	| Update a location's details |
| /locations/<location_id>	| DELETE	| Delete a location |
| /rentals	| GET	| List all rental |
| /rentals	| POST	| Add a new rental |
| /rentals/<rental_id>	| PUT	| Update a rental's details |
| /rentals/<rental_id>	| DELETE	| Delete a rental |

## Git Commit Guidelines
Use conventional commits:
```bash
feat: add user authentication
fix: resolve database connection issue
docs: update API documentation
test: add user registration tests
```
