def get_current_user(session):
   # Check if "user_id" exists in the session
    if "user_id" in session:
      # Retrieve the user_id from the session
        user_id = session["user_id"]
      # Return the user_id
        return user_id
    else:
      # If "user_id" does not exist in the session, return None
        return None
