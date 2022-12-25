from flask_app import app
from flask import render_template, request, redirect, session
from flask import flash
from flask_app.models.user import User

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register/user", methods=["POST"])
def register():
    valid_user = User.create_valid_user(request.form)

    if not valid_user:
        return redirect("/")
    
    session["user_id"] = valid_user.id
    
    return redirect("/sightings/home")

@app.route("/login", methods=["POST"])
def login():
    valid_user = User.authenticated_user_by_input(request.form)
    if not valid_user:
        return redirect("/")

    session["user_id"] = valid_user.id
    return redirect("/sightings/home")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

