from flask import Flask, render_template, request, session, redirect, url_for
from helper import get_current_user
from database import (
  load_distinct_cities,
  load_room_type,
  login_user,
  register_user,
  search_for_rooms,
  load_room_info,
  book_room,
  get_room_type_per_room,
  get_user_reviews,
  add_user_review,
  calculate_review_rate,
  get_booked_rooms_from_user,
  get_reviews_per_user,
  search_for_rooms_extra,
  calculate_total_price,
)

app = Flask(__name__)
app.secret_key = "your secret key"


# Index page
@app.route("/")
def hello_world():
  # Get all distinct cities for the select input
  cities = load_distinct_cities()
  # Get all distict room types and values
  room_type = load_room_type()
  return render_template("index.html", cities=cities, room_type=room_type)


# Sign in Page
@app.route("/signin", methods=["GET", "POST"])
def login_page():
  return render_template("signin.html")


# Login Action - POST Button
@app.route("/login", methods=["POST"])
def login_action():
  msg = ""
  # Retrieve the username and password from the form data
  username = request.form["username"]
  password = request.form["password"]
  # Call the login_user function to check user credentials
  info = login_user(username, password)
  if info:
    # Retrieve the user_id from the first item in the 'info' list
    test = info[0]["user_id"]

    # Store the user_id in the session
    session["user_id"] = info[0]["user_id"]
    # Set 'loggedin' to True in the session
    session["loggedin"] = True
    msg = "Logged in successfully!"
    return redirect(url_for("profile_page"))
  else:
    # If the login fails, set the error message
    msg = "Incorrect username / password!"
  return render_template("signin.html", info=info, msg=msg)


# Profile Page
@app.route("/profile")
def profile_page():
  #Retrieve the user_id from the session
  user_id = get_current_user(session)
  if user_id is not None:
    # Retrieve the booked rooms for the user
    booked_rooms = get_booked_rooms_from_user(user_id)

    # Retrieve the reviews submitted by the user
    user_reviews = get_reviews_per_user(user_id)

    # Render the profile.html template with the booked_rooms and user_reviews variables
    return render_template("profile.html",
                           booked_rooms=booked_rooms,
                           user_reviews=user_reviews)
  else:
    # If the user is not logged in, redirect to the login_page route
    return redirect(url_for("login_page"))


# Register Page
@app.route("/register")
def register_page():
  return render_template("register.html")


# Register Action - POST Button
@app.route("/register", methods=["POST"])
def register():
  message = ""
  # Retrieve the name, email, and password from the form data
  username = request.form["name"]
  email = request.form["email"]
  password = request.form["password"]

  # Call the register_user function to register the user
  message = register_user(username, email, password)
  return render_template("register.html", msg=message)


# Room List Page - After Getting the data from the FORM
@app.route("/room_list", methods=["GET"])
def search_rooms():
  # Get data from the form
  city = request.args.get("city")
  room_type = request.args.get("room_type")
  checkin_date = request.args.get("checkin_date")
  checkout_date = request.args.get("checkout_date")
  # Save data to session for later use
  session["city"] = city
  session["room_type"] = room_type
  session["checkin_date"] = checkin_date
  session["checkout_date"] = checkout_date
  # Perform a search for available rooms based on the provided data
  search = search_for_rooms(city, room_type, checkin_date, checkout_date)
  # Retrieve necessary data for the aside form
  distinct_cities = load_distinct_cities()
  distinct_room_types = load_room_type()
  room_type_descr = get_room_type_per_room(room_type)

  # Render the room_list.html template with the search results and necessary data
  return render_template(
    "room_list.html",
    search=search,
    room_type_descr=room_type_descr,
    city=city,
    room_type=room_type,
    checkin_date=checkin_date,
    checkout_date=checkout_date,
    distinct_cities=distinct_cities,
    distinct_room_types=distinct_room_types,
  )


# Room Page
@app.route("/room_page/<room_id>")
def show_room(room_id):
  # # Get data from the database for the selected room
  room_info = load_room_info(room_id)
  user_id = get_current_user(session)
  type_of_room = get_room_type_per_room(room_id)
  user_reviews = get_user_reviews(room_id)
  users_rating = calculate_review_rate(room_id)
  # Get data from session
  city = session["city"]
  room_type = session["room_type"]
  checkin_date = session["checkin_date"]
  checkout_date = session["checkout_date"]
  return render_template(
    "room_page.html",
    room_id=room_id,
    room_info=room_info,
    user_id=user_id,
    city=city,
    room_type=room_type,
    checkin_date=checkin_date,
    checkout_date=checkout_date,
    type_of_room=type_of_room,
    user_reviews=user_reviews,
    users_rating=users_rating,
  )


# Booking Action
@app.route("/room_page/<room_id>/booking", methods=["POST"])
def booking_room(room_id):
  # Get data from session
  checkin_date = session["checkin_date"]
  checkout_date = session["checkout_date"]
  # Calculate total price
  total_price = calculate_total_price(room_id, checkin_date, checkout_date)
  user_id = get_current_user(session)
  message = ""
  if user_id is None:
    # If user is not connected then write the message
    message = "Sign in or create a free account to plan your trip"
    return render_template("sumbit.html", message=message)
  else:
    # If user is connected the insert data to database
    message = "We are thrilled to inform you that your hotel reservation has been successfully booked"
    res = book_room(user_id, room_id, checkin_date, checkout_date, total_price)
    return render_template("sumbit.html", res=res, message=message)


# Review Action - POST a Review
@app.route("/room_page/<room_id>/review", methods=["POST"])
def review_room(room_id):
  # Check if user is connected
  user_id = get_current_user(session)
  message = ""
  # Get data from the form
  rate = request.form["rating"]
  comment = request.form.get("comment", "")
  if user_id is None:
    # If user is not connected then write the message
    message = "Sign in or create a free account to make a review"
    return render_template("sumbit.html", message=message)
  else:
    message = "Thank you for the comment"
    # If user is connected insert the data to database
    res = add_user_review(user_id, room_id, rate, comment)
    return render_template("sumbit.html", message=message)


# Aside bar Search from the List page
@app.route("/new_room_list", methods=["GET"])
def search_rooms_sidebar():
  # Get data from FORM
  city = request.args.get("city")
  room_type = request.args.get("room_type")
  checkin_date = request.args.get("checkin_date")
  checkout_date = request.args.get("checkout_date")
  min_price = request.args.get("min")
  max_price = request.args.get("max")
  # Save data to session
  session["city"] = city
  session["room_type"] = room_type
  session["checkin_date"] = checkin_date
  session["checkout_date"] = checkout_date
  search = search_for_rooms_extra(city, room_type, checkin_date, checkout_date,
                                  min_price, max_price)
  # Get data for the aside search bar
  distinct_cities = load_distinct_cities()
  distinct_room_types = load_room_type()
  room_type_descr = get_room_type_per_room(room_type)
  return render_template(
    "room_list.html",
    search=search,
    room_type_descr=room_type_descr,
    city=city,
    room_type=room_type,
    checkin_date=checkin_date,
    checkout_date=checkout_date,
    distinct_cities=distinct_cities,
    distinct_room_types=distinct_room_types,
  )


# Testing route
# @app.route("/test/<room_id>", methods=["GET"])
# def testing(room_id):
#     checkin_date = session["checkin_date"]
#     checkout_date = session["checkout_date"]
#     price = calculate_total_price(room_id, checkin_date, checkout_date)
#     return render_template("test.html", price=price)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5055, debug=True)
