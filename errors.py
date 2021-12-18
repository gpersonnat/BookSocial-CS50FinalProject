from flask import redirect, render_template, session
from functools import wraps



# Returns error message
def error(message, route, code=400):
    return render_template("error.html", message=message, code=code, route=route), code

# Ensures that user is logged in
def login_required(f):
    """https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/ """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

