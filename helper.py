def get_current_user(session):
    if "user_id" in session:
        user_id = session["user_id"]
        return user_id
    else:
        return None
