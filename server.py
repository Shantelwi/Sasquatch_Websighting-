from flask_app import app
from flask_app.controllers import users,sightings
from flask import Flask,request,redirect,session,render_template

if __name__ == "__main__":
    app.run(debug=True)