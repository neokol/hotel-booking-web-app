from sqlalchemy import create_engine
from sqlalchemy import text
import json
from datetime import datetime
import os

db_connection_string = os.environ["DB_CONNECTION_STRING"]

engine = create_engine(db_connection_string,
                       connect_args={"ssl": {
                         "ssl_ca": "/etc/ssl/cert.pem"
                       }})


# Function to get  distinct cities for the select
def load_distinct_cities():
  # Connect to the database engine
  with engine.connect() as conn:
    # Execute a SQL query to retrieve distinct cities from the 'room' table
    result = conn.execute(text("SELECT DISTINCT city FROM room"))

    # Fetch all the cities returned by the query
    result_all_cities = result.all()
    return result_all_cities


# Function to get room type for the select
def load_room_type():
  with engine.connect() as conn:
    # Execute a SQL query to retrieve distinct room types from the 'room_type' table
    result = conn.execute(text("SELECT * FROM room_type"))
    results_list = result.all()
    result_all_room_type = dict(results_list)
    return result_all_room_type


# Function to Login the user - check if the credentials are correct
def login_user(name, pswd):
  with engine.connect() as conn:
     # Define the SQL query with placeholders for email and password
    query = text(
      "SELECT * FROM user WHERE email = :email AND password = :pswd")
    result = conn.execute(query, {"email": name, "pswd": pswd})
     # Fetch all the rows returned by the query
    user = result.all()
     # Check if any rows were returned
    if result:
      # Convert the rows to a list of dictionaries for easier access
      user_as_dict = [u._asdict() for u in user]
      return user_as_dict
    else:
      # If no rows were returned, return None
      return None


# Function to post user data to user table and register the user
def register_user(name, email, password):
  with engine.connect() as conn:
    msg = ""
    # Check if an account with the provided email already exists
    check_query = text("SELECT * FROM user WHERE email = :email")
    insert_query = text(
      "INSERT INTO user (name,email,password) VALUES (:name, :email, :password)"
    )
    check_result = conn.execute(check_query, {"email": email})
    account = check_result.fetchone()
    # If an account exists, set the message to indicate it
    if account:
      msg = "Account already exists"
    else:
      # Insert a new user into the 'user' table
      conn.execute(insert_query, {
        "name": name,
        "email": email,
        "password": password
      })
      # Commit the changes to the database
      conn.commit()
      # Set the message to indicate successful registration
      msg = "You have successfully registered"
    return msg


# Get the results of the search of the user
def search_for_rooms(city, room_type, checkin_date, checkout_date):
  with engine.connect() as conn:
    query = text(
      "SELECT * FROM room WHERE city = :city AND type_id = :room_type AND room_id NOT IN (SELECT room_id FROM booking WHERE check_in_date <= :checkin AND check_out_date >= :checkout)"
    )
    cur = conn.execute(
      query,
      {
        "city": city,
        "room_type": room_type,
        "checkin": checkin_date,
        "checkout": checkout_date,
      },
    )
    data = cur.all()
    # convert data to dictionary
    search_results = [u._asdict() for u in data]

    return search_results


# Get the results of the search in list page - with extra like price
def search_for_rooms_extra(city, room_type, checkin_date, checkout_date,
                           min_price, max_price):
  with engine.connect() as conn:
    query = text(
      "SELECT * FROM room WHERE city = :city AND type_id = :room_type AND price >= :min_price AND price <= :max_price AND room_id NOT IN (SELECT room_id FROM booking WHERE check_in_date <= :checkin AND check_out_date >= :checkout)"
    )
    cur = conn.execute(
      query,
      {
        "city": city,
        "room_type": room_type,
        "checkin": checkin_date,
        "checkout": checkout_date,
        "min_price": min_price,
        "max_price": max_price,
      },
    )
    data = cur.all()
    # convert data to dictionary
    search_results = [u._asdict() for u in data]

    return search_results


# Load all room information with the room_id
def load_room_info(room_id):
  with engine.connect() as conn:
    query = text("SELECT * FROM room WHERE room_id = :room_id")
    result = conn.execute(query, {"room_id": room_id})
    rows = result.all()
    if len(rows) == 0:
      return None
    else:
      return [u._asdict() for u in rows]


# Function to book room
def book_room(user_id, room_id, checkin_date, checkout_date, total_price):
  with engine.connect() as conn:
    query = text(
      "INSERT INTO booking (user_id, room_id, check_in_date, check_out_date, total_price) VALUES (:user_id, :room_id, :checkin_date,:checkout_date, :total_price)"
    )
    res = conn.execute(
      query,
      {
        "user_id": user_id,
        "room_id": room_id,
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "total_price": total_price,
      },
    )
    # Use commit to finilize the booking
    conn.commit()
    return res


# function to get the title from the room type (Single room, double room etc.)
def get_room_type_per_room(room_id):
  with engine.connect() as conn:
    query = text("SELECT title FROM room_type WHERE type_id = :room_id")
    result = conn.execute(query, {"room_id": room_id})
    descriptions = [row[0] for row in result.fetchall()]
    return descriptions


# def make_favorite_room(user_id, room_id):
#     with engine.connect() as conn:
#         query = text(
#             "INSERT INTO favorite (user_id, room_id) VALUES (:user_id, :room_id)"
#         )
#         res = conn.execute(query, {"user_id": user_id, "room_id": room_id})
#         conn.commit()
#         return res


# function to get all reviews from a room
def get_user_reviews(room_id):
  with engine.connect() as conn:
    query = text(
      "SELECT R.comment, U.name FROM review R LEFT JOIN user U ON R.user_id = U.user_id WHERE room_id = :room_id"
    )
    res = conn.execute(query, {"room_id": room_id})
    reviews = res.all()
    reviews_users = [u._asdict() for u in reviews]
    if len(reviews_users) > 0:
      return reviews_users
    else:
      return None


# Funtion to post a review from a selected user
def add_user_review(user_id, room_id, rate, comment):
  with engine.connect() as conn:
    query = text(
      "INSERT INTO review (user_id, room_id, rate, comment) VALUES (:user_id, :room_id, :rate, :comment)"
    )
    res = conn.execute(
      query,
      {
        "user_id": user_id,
        "room_id": room_id,
        "rate": rate,
        "comment": comment
      },
    )
    conn.commit()
    return res


# function to calculate the average rate of a room
def calculate_review_rate(room_id):
  with engine.connect() as conn:
    query = text("SELECT rate FROM review WHERE room_id = :room_id")
    res = conn.execute(query, {"room_id": room_id})
    res_rating = [row[0] for row in res.fetchall()]
    if len(res_rating) > 0:
      rating_average = sum(res_rating) / len(res_rating)
      return rating_average
    else:
      return 0


# Get Booked rooms from a selected user
def get_booked_rooms_from_user(user_id):
  with engine.connect() as conn:
    query = text(
      "SELECT B.room_id, B.room_id, B.check_in_date, B.check_out_date,B.total_price, R.name, R.city, R.area, R.photo_url, R.description_short FROM booking B LEFT JOIN room  R ON R.room_id = B.room_id WHERE B.user_id = :user_id"
    )
    res = conn.execute(
      query,
      {"user_id": user_id},
    )
    booked_rooms = [u._asdict() for u in res.fetchall()]
    return booked_rooms


# Get all reviews from a selected user
def get_reviews_per_user(user_id):
  with engine.connect() as conn:
    query = text(
      "SELECT A.rate,B.name FROM review A LEFT JOIN  room B ON  A.room_id = B.room_id WHERE user_id = :user_id"
    )
    res = conn.execute(query, {"user_id": user_id})
    user_reviews = [u._asdict() for u in res.fetchall()]
    return user_reviews


# Function to calculate the total price of a book reservation
def calculate_total_price(room_id, checkin_date, checkout_date):
  with engine.connect() as conn:
    query = text("SELECT price FROM room WHERE room_id = :room_id")
    result = conn.execute(query, {"room_id": room_id})
    # fetch the only one data get from the query
    price_per_day = result.fetchone()[0]
    # convert str to datetime
    check_in_date = datetime.strptime(checkin_date, "%Y-%m-%d")
    check_out_date = datetime.strptime(checkout_date, "%Y-%m-%d")
    # calculate the number of days
    stay_duration = (check_out_date - check_in_date).days
    # Calulate the total price
    total_price = stay_duration * price_per_day
    return total_price
