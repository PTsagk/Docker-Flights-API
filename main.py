# Installed
from flask import *

# Installed
from pymongo import MongoClient

from bson import ObjectId, json_util

import json


# Connect to mongodbContainer
client = MongoClient("mongodb://localhost:27017")

# Access the databasae Digital Airlines
db = client["DigitalAirlines"]

# Access the collections
usersCollection = db["users"]
flightsCollection = db["flights"]
reservationsCollection = db["reservations"]


def insertAdmin():
    # Check if there are any users in the users collection
    usersCount = usersCollection.count_documents({})

    # If there are no users then the database is empty and we should insert the admin
    if usersCount == 0:
        usersCollection.insert_one(
            {
                "_id": ObjectId("64918ffabdcd8fc0c87304ce"),
                "username": "admin",
                "surname": "admin",
                "email": "admin@gmail.com",
                "password": "admin123",
                "date": "2002",
                "country": "Greece",
                "passport_number": "1234567890",
            }
        )


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    # usersCount = usersCollection.count_documents({})
    users = usersCollection.find({})
    return json.loads(json_util.dumps(users))


# Register endpoint
@app.route("/register", methods=["POST"])
def register():
    # Access the parameters in body
    try:
        username = request.json["username"]
        surname = request.json["surname"]
        email = request.json["email"]
        password = request.json["password"]
        birthDate = request.json["birthDate"]
        country = request.json["country"]
        passportNumber = request.json["passportNumber"]

    # If one is missing return bad request response
    except:
        return Response("All fields are required", status=400)

    # Check if there is somene with the same username or email already in the database
    found = usersCollection.count_documents(
        {"$or": [{"username": username}, {"email": email}]}
    )

    # If user with this email or username was found return conflict status code
    if found > 0:
        return Response("User with this username or email is already found", status=409)

    # Also if parameters are empty
    if (
        username == ""
        or surname == ""
        or email == ""
        or password == ""
        or birthDate == ""
        or country == ""
        or passportNumber == ""
    ):
        # Return the same response
        return Response("All fields are required", status=400)
    # Try to insert in the database the new user
    try:
        usersCollection.insert_one(
            {
                "username": username,
                "surname": surname,
                "email": email,
                "password": password,
                "birth_date": birthDate,
                "country": country,
                "passport_number": passportNumber,
            }
        )

        # If every goes well return success
        return Response("Account created successfully", status=200)
    except:
        # Else return internal server error response
        return Response("Something went wrong", status=500)


# Login endpoint
@app.route("/login", methods=["POST"])
def login():
    # Access body parameters
    try:
        email = request.json["email"]
        password = request.json["password"]

    # If one fails the something is missing so return bad request
    except:
        return Response("All fields are required", status=400)

    try:
        # Check if user with this email and password exists
        user = usersCollection.find_one({"email": email, "password": password})

        # Else return unauthorized status code
        if user is None:
            return Response("Email or password is incorrect", status=401)

        # If user found send cookie with value the id of the user account in mongo db
        response = make_response("Login Succesful")
        response.set_cookie("userID", str(ObjectId(user["_id"])))
        response.status = 200
        return response

    # If something of the above action fails it's mongodb action problem so return insernal server error status code
    except:
        return Response("Something went wrong", status=500)


# This function is called in all bellow requests of the user to check if he is logged in (like middleware)
def checkAuthentication(request):
    # Get user id from cookie
    userId = request.cookies.get("userID")

    # If user found in mongo db with this id return the userId else return None
    found = usersCollection.count_documents({"_id": ObjectId(userId)})
    if found > 0:
        return userId
    else:
        return None


# Logout endpoint
@app.route("/logout", methods=["GET"])
def logout():
    try:
        # Set cookie to empty value and expiration 0 seconds
        response = make_response("Logout successfull")
        response.set_cookie("userID", "", expires=0)
        response.status = 200
        return response

    except:
        # If something above fails return internal server error status code
        Response("Something went wrong")


# Search for available flights
@app.route("/flights", methods=["GET"])
def getFlights():
    try:
        # Check if user is logged in and get the cookie value (_id in mongo database)
        userID = checkAuthentication(request)

        # If userID found
        if not userID:
            # If userID is None that means the cookie not found or it's value is invalid so authentication failed
            # Return unauthorized status code
            return Response("You must login", status=401)

        # Get values from query
        depart = request.args.get("depart")
        destination = request.args.get("destination")
        date = request.args.get("date")

        # If depart, destination and date is given in the query search based on this
        if depart is not None and destination is not None and date is not None:
            flights = flightsCollection.find(
                {
                    "depart_airport": depart,
                    "destination_airport": destination,
                    "date": date,
                },
                {
                    "economy_count": 0,
                    "business_count": 0,
                    "economy_cost": 0,
                    "business_cost": 0,
                },
            )

        # Else if depart and destination is given in the query search based on this
        elif depart is not None and destination is not None:
            flights = flightsCollection.find(
                {"depart_airport": depart, "destination_airport": destination},
                {
                    "economy_count": 0,
                    "business_count": 0,
                    "economy_cost": 0,
                    "business_cost": 0,
                },
            )

        # Else if date only is given in the query search based on this
        elif date is not None:
            flights = flightsCollection.find({"date": date})

        # Else if nothing is given return all the flights
        else:
            # Find all flights but don't give the information about economy_count, bussiness_count, economy_cost and business_cost
            flights = flightsCollection.find(
                {},
                {
                    "economy_count": 0,
                    "business_count": 0,
                    "economy_cost": 0,
                    "business_cost": 0,
                },
            )

        # Return the result is json format
        return json.loads(json_util.dumps(flights))

    # If something of the above fails is mongodb action problem so reutrn internal server error status code
    except:
        Response("Something went wrong", status=500)


# Flight details endpoint
@app.route("/flights/information", methods=["GET"])
def getFlightInformation():
    try:
        # Check if user is logged in and get the cookie value (_id in mongo database)
        userID = checkAuthentication(request)
        if not userID:
            return Response("You must login", status=401)

        # Get flight_id from query
        flight_id = request.args.get("flight_id")

        # Search for the flight with this id
        flight = flightsCollection.find({"_id": ObjectId(flight_id)})

        return json.loads(json_util.dumps(flight))

    except:
        return Response("Something went wrong", status=500)


# Reserve flight endpoint
@app.route("/reservations/create", methods=["POST"])
def reserve_flight():
    # Check if the logged in user is the admin because admin can't make reservations
    userID = checkAdminAuthentication(request)
    if userID:
        return Response("Admin can't make reservations", status=400)

    userID = checkAuthentication(request)
    if not userID:
        # Get the parameters from body
        return Response("You must login", status=401)
    try:
        username = request.json["username"]
        surname = request.json["surname"]
        passportNumber = request.json["passportNumber"]
        birthDate = request.json["birthDate"]
        email = request.json["email"]
        reservationType = request.json["reservationType"]

    # If at least one is missing return bad request status code
    except:
        return Response("All fields are required", status=400)

    try:
        # If there paramaters exist but at least one is empty return again bad requests status code
        if (
            username == ""
            or surname == ""
            or passportNumber == ""
            or birthDate == ""
            or email == ""
            or reservationType == ""
        ):
            return Response("All fields are required", status=400)
        # Else if inputs are correct

        flight_id = request.args.get("flight_id")
        # If reservation type is business decrease the amount of availabe business tickets for this flight
        if reservationType == "business":
            updatedReservation = flightsCollection.find_one_and_update(
                {"_id": ObjectId(flight_id), "business_count": {"$gt": 0}},
                {"$inc": {"business_count": -1}},
            )

            # If updatedReservation is None no update was made so the flight was found with this id
            if updatedReservation is None:
                return Response(
                    "No available business tickets found or wrong flight_id provided",
                    status=404,
                )

        # Else if reservation type is economy decrease the amount of available economy tickets for this flight
        else:
            updatedReservation = flightsCollection.find_one_and_update(
                {"_id": ObjectId(flight_id), "economy_count": {"$gt": 0}},
                {"$inc": {"economy_count": -1}},
            )
            if updatedReservation is None:
                return Response(
                    "No available economy tickets found or wrong flight_id provided",
                    status=404,
                )

        # add the reservation to the reservation collection
        reservationsCollection.insert_one(
            {
                "user_id": userID,
                "flight_id": flight_id,
                "username": username,
                "surname": surname,
                "passport_number": passportNumber,
                "birth_date": birthDate,
                "email": email,
                "reservation_type": reservationType,
            }
        )
        return Response("Reservation completed", status=200)
    # If something else went wrong it's probably because of mongodb fail so return internal server error resonse code
    except:
        return Response("Something went wrong", status=500)


# User reservations endpoint
@app.route("/reservations", methods=["GET"])
def getReservations():
    try:
        # Check if the logged in user is the admin because admin can't make reservations
        userID = checkAdminAuthentication(request)
        if userID:
            return Response("Admin can't make reservations", status=400)

        userID = checkAuthentication(request)
        if not userID:
            return Response("You must login", status=401)

        # Find all reservations where user_id is the userID from cookie and display only the flight_id
        reservations = reservationsCollection.find(
            {"user_id": userID}, {"flight_id": 1}
        )
        return json.loads(json_util.dumps(reservations))

    except:
        return Response("Something went wrong", status=500)


# Details for specific reservation
@app.route("/reservations/details", methods=["GET"])
def getReservationsDetails():
    try:
        # Check if the logged in user is the admin because admin can't make reservations
        userID = checkAdminAuthentication(request)
        if userID:
            return Response("Admin can't make reservations", status=400)
        userID = checkAuthentication(request)
        if not userID:
            return Response("You must login", status=401)
        # Get the reservation id from the query
        reservation_id = request.args.get("reservation_id")

        # Find the reservation with the specific id and the user_id is the same with the one that is logged in right now
        reservationInfo = reservationsCollection.find_one(
            {"_id": ObjectId(reservation_id), "user_id": userID},
            {"_id": 0},  # Don't show _id
        )
        flightInfo = flightsCollection.find_one(
            {"_id": ObjectId(reservationInfo["flight_id"])},
            {"_id": 0, "depart_airport": 1, "destination_airport": 1, "date": 1},
        )
        return jsonify(reservationInfo, flightInfo)

    except:
        return Response("Something went wrong", status=500)


# Cancel reservation endpoint
@app.route("/reservations/cancel", methods=["DELETE"])
def cancelReservation():
    try:
        # Check if the logged in user is the admin because admin can't make reservations
        userID = checkAdminAuthentication(request)
        if userID:
            return Response("Admin can't make reservations", status=400)

        userID = checkAuthentication(request)
        if not userID:
            return Response("You must login", 401)
        # Get the reservation_id from the query
        reservation_id = request.args.get("reservation_id")

        # Delete the reservation from the database
        canceledReservation = reservationsCollection.find_one_and_delete(
            {"_id": ObjectId(reservation_id)}
        )

        # If no reservation with this id found return not found status code
        if canceledReservation is None:
            return Response("No reservation with this id found", status=404)

        # If canceled reservation type is business increase the amount of available business tickets
        if canceledReservation["reservation_type"] == "business":
            updatedFlight = flightsCollection.find_one_and_update(
                {"_id": ObjectId(canceledReservation["flight_id"])},
                {"$inc": {"businessCount": 1}},
            )

            # If no flight was updated then the flight id was incorrect
            if updatedFlight is None:
                return Response("Flight with this id was not found", status=404)

        # If canceled reservation type is economy increase the amount of available economy tickets
        else:
            updatedFlight = flightsCollection.find_one_and_update(
                {"_id": ObjectId(canceledReservation["flight_id"])},
                {"$inc": {"economy_count": 1}},
            )

            # If no flight was updated then the flight id was incorrect
            if updatedFlight is None:
                return Response("Flight with this id was not found", status=404)

        return Response("Reservation canceled", status=200)

    except:
        return Response("Something went wrong", status=500)


# Delete user account endpoint
@app.route("/users/delete", methods=["DELETE"])
def deleteUser():
    try:
        # Check if the logged in user is the admin because admin can't make reservations
        userID = checkAdminAuthentication(request)
        if userID:
            return Response("Admin account can't be deleted", status=400)
        userID = checkAuthentication(request)
        if not userID:
            return Response("You must login", 401)
        # Delete user from database
        deletedUser = usersCollection.find_one_and_delete({"_id": ObjectId(userID)})

        # If user found and deleted return success
        if deletedUser is not None:
            response = make_response("Your account was deleted succesfully")
            response.set_cookie("userID", "", expires=0)
            response.status = 200
            return response
        else:
            return Response("Account id not found", status=404)

    except:
        return Response("Something went wrong", status=500)


# -----------------------------------------Admin routes----------------------------------------------------


# This will be called to validate that the cookie has the value of Admin id in the database
def checkAdminAuthentication(request):
    userID = request.cookies.get("userID")

    # Compare to admin id and if it's the same return the id
    if userID == "64918ffabdcd8fc0c87304ce":
        return userID
    return None


# Create a flight endpoint
@app.route("/flights/create", methods=["POST"])
def createFlight():
    # Check if the cookie has the id of the admin
    adminID = checkAdminAuthentication(request)

    # If id is None the admin is not authenticated
    if not adminID:
        return Response("You are not the admin", status=401)
    # Try to get the body parameters
    try:
        departAirport = request.json["departAirport"]
        destinationAirport = request.json["destinationAirport"]
        date = request.json["date"]
        economyCost = request.json["economyCost"]
        businessCost = request.json["businessCost"]
        economyCount = request.json["economyCount"]
        businessCount = request.json["businessCount"]

    # If at least one is missing reutrh the bad requests status code
    except:
        return Response("All fields are required", status=400)

    # Check also if the parameters exists but are empty
    if (
        departAirport == ""
        or destinationAirport == ""
        or date == ""
        or economyCost == ""
        or businessCost == ""
        or economyCount == ""
        or businessCount == ""
    ):
        return Response("All fields are required", status=400)
    try:
        # Insert flight to database
        flightsCollection.insert_one(
            {
                "depart_airport": departAirport,
                "destination_airport": destinationAirport,
                "date": date,
                "economy_cost": economyCost,
                "business_cost": businessCost,
                "economy_count": economyCount,
                "business_count": businessCount,
            }
        )
        return Response("Flight created successfully", status=200)
    except:
        return Response("Something went wrong", status=500)


# Change cost for tickets in a specific flight
@app.route("/flights/change_cost", methods=["PATCH"])
def changeCost():
    adminID = checkAdminAuthentication(request)
    if not adminID:
        return Response("You are not the admin", status=401)
    # Get the flight id from the query
    flight_id = request.args.get("flight_id")

    # Check if flight exists
    flight = flightsCollection.find_one({"_id": ObjectId(flight_id)})

    # If flight exists try getting the economy ticket cost from the body
    if flight:
        try:
            newEconomyCost = request.json["economyCost"]

        # If it wasn't given in the parameters set it to None
        except:
            newEconomyCost = None

        # If it's not none then the admin want's to change the cost for economy ticket
        if newEconomyCost:
            try:
                flightsCollection.find_one_and_update(
                    {"_id": ObjectId(flight_id)},
                    {"$set": {"economy_cost": newEconomyCost}},
                )
            except:
                return Response("Something went wrong", status=500)

        # The same for the business ticket cost
        try:
            newBusinessCost = request.json["businessCost"]
        except:
            newBusinessCost = None

        if newBusinessCost:
            try:
                flightsCollection.find_one_and_update(
                    {"_id": ObjectId(flight_id)},
                    {"$set": {"business_cost": newBusinessCost}},
                )
            except:
                return Response("Something went wrong", status=500)

        return Response("Costs updated successfully", status=200)
    else:
        return Response("Flight with this id not found", status=404)


# Delete flight enpoint
@app.route("/flights/delete", methods=["DELETE"])
def deleteFlight():
    adminID = checkAdminAuthentication(request)
    if not adminID:
        return Response("You are not the admin", status=401)

    flight_id = request.args.get("flight_id")

    # Try to find at least one reservation with this flight_id
    reservation = reservationsCollection.find_one({"flight_id": flight_id})

    # If no reservation was found then we can delete this flight
    if not reservation:
        deletedFlight = flightsCollection.find_one_and_delete(
            {"_id": ObjectId(flight_id)}
        )
        if deletedFlight:
            return Response("Flight deleted successfully", status=200)
        else:
            return Response("No flight found with this id", status=404)

    # Else the flight has reservations so we return conflict status code
    else:
        return Response(
            "This flight has reservations so it cannot be deleted", status=409
        )


@app.route("/flights/admin/info", methods=["GET"])
def getFlightInfo():
    try:
        adminID = checkAdminAuthentication(request)
        if not adminID:
            return Response("You are not the admin", status=401)
        flight_id = request.args.get("flight_id")

        # Check if fligh exists
        flight = flightsCollection.find_one({"_id": ObjectId(flight_id)}, {"_id": 0})

        # If flight exists find all reservations with the same flight_id
        if not flight:
            return Response("No flight found with this id", status=404)
        reservations = reservationsCollection.find(
            {"flight_id": flight_id},
            {
                "username": 1,
                "surname": 1,
                "reservation_type": 1,
                "_id": 0,
            },  # From the reservations display only the username, surname and the reservation_type
        )
        if not reservations:
            return Response("No reservetions found for this flight")

        print(reservations)
        totalTickets = 0
        economyTicketsCount = 0
        businessTicketsCount = 0
        # Format the result in json format
        output = []
        for reservation in reservations:
            totalTickets += 1
            if reservation["reservation_type"] == "economy":
                economyTicketsCount += 1
            else:
                businessTicketsCount += 1
            output.append(reservation)
        return jsonify(
            flight,
            {
                "total tickets": totalTickets,
                "total economy tickets booked": economyTicketsCount,
                "total business tickets booked": businessTicketsCount,
            },
            output,
        )

    except:
        return Response("Something went wrong", status=500)


if __name__ == "__main__":
    insertAdmin()
    app.run(debug=True, host="0.0.0.0", port=5000)
