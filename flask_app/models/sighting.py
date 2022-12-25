from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

DB = "sasquatch_websiting"

class Sighting:
    def __init__(self, data):
        self.id = data['id']
        self.location = data['location']
        self.what_happened = data['what_happened']
        self.num_of_sasquatches = data['num_of_sasquatches']
        self.date_of_sighting = data['date_of_sighting']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user = None

    @classmethod
    def create_valid_sighting(cls, sighting_dict):
        if not cls.is_valid(sighting_dict):
            return False
        
        query = """INSERT INTO sightings (location, what_happened, num_of_sasquatches,
                    date_of_sighting, user_id) VALUES (%(location)s,
                    %(what_happened)s, %(num_of_sasquatches)s,
                    %(date_of_sighting)s, %(user_id)s);"""
        sighting_id = connectToMySQL(DB).query_db(query, sighting_dict)
        sighting = cls.get_by_id(sighting_id)

        return sighting

    @classmethod
    def get_by_id(cls, sighting_id):
        data = {"id": sighting_id}
        query = """SELECT sightings.id, sightings.created_at, 
                sightings.updated_at, location, what_happened, date_of_sighting, 
                num_of_sasquatches,
                    users.id as user_id, first_name, last_name, password,
                    email, users.created_at as uc, users.updated_at as uu
                    FROM sightings
                    JOIN users on users.id = sightings.user_id
                    WHERE sightings.id = %(id)s;"""
        
        result = connectToMySQL(DB).query_db(query,data)
        result = result[0]
        sighting = cls(result)
        
        sighting.user = user.User(
                {
                    "id": result["user_id"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "email": result["email"],
                    "password": result["password"],
                    "created_at": result["uc"],
                    "updated_at": result["uu"]
                }
            )

        return sighting

    @classmethod
    def delete_sighting_by_id(cls, sighting_id):

        data = {"id": sighting_id}
        query = "DELETE from sightings WHERE id = %(id)s;"
        connectToMySQL(DB).query_db(query,data)

        return sighting_id


    @classmethod
    def update_sighting(cls, sighting_dict, session_id):

        sighting = cls.get_by_id(sighting_dict["id"])
        if sighting.user.id != session_id:
            flash("You must be the creator to update this sighting.")
            return False

        # Validate the input
        if not cls.is_valid(sighting_dict):
            return False
        
        # Update the data in the database.
        query = """UPDATE sightings
                    SET location = %(location)s, what_happened = %(what_happened)s, 
                    date_of_sighting = %(date_of_sighting)s, num_of_sasquatches = %(num_of_sasquatches)s
                    WHERE id = %(id)s;"""
        result = connectToMySQL(DB).query_db(query,sighting_dict)
        sighting = cls.get_by_id(sighting_dict["id"])
        
        return sighting

    @classmethod
    def get_all(cls):
        # Get all recipes, and the user info for the creators
        query = """SELECT 
                    sightings.id, sightings.created_at, sightings.updated_at, 
                    location, what_happened, date_of_sighting, num_of_sasquatches,
                    users.id as user_id, first_name, last_name, email, password, 
                    users.created_at as uc, users.updated_at as uu
                    FROM sightings
                    JOIN users on users.id = sightings.user_id;"""
        sighting_data = connectToMySQL(DB).query_db(query)

        sightings = []

        # Iterate through the list of recipe dictionaries
        for sighting in sighting_data:

            # convert data into a recipe object
            sighting_obj = cls(sighting)

            # convert joined user data into a user object
            sighting_obj.user = user.User(
                {
                    "id": sighting["user_id"],
                    "first_name": sighting["first_name"],
                    "last_name": sighting["last_name"],
                    "email": sighting["email"],
                    "password": sighting["password"],
                    "created_at": sighting["uc"],
                    "updated_at": sighting["uu"]
                }
            )
            sightings.append(sighting_obj)


        return sightings

    @staticmethod
    def is_valid(sighting_dict):
        valid = True
        flash_string = " field is required and must be at least 3 characters."
        if len(sighting_dict["location"]) < 3:
            flash("location " + flash_string)
            valid = False
        if len(sighting_dict["what_happened"]) < 3:
            flash("what_happened " + flash_string)
            valid = False
        if len(sighting_dict["date_of_sighting"]) <= 0:
            flash("Date is required.")
            valid = False
        if "num_of_sasquatches" not in sighting_dict:
            flash("How many Sasquatches were sighted")
            valid = False

        return valid
