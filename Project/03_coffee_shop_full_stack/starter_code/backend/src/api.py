import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['GET'])
# @requires_auth(permission="get:drinks")
def drinks():
    drinks = Drink.query.all()
    short_drinks = [drink.short() for drink in drinks]
    if not drinks:
        abort(404)
    
    return jsonify({
        # "status_code": 200,
        "success": True,
        "drinks":short_drinks
    })


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=['GET'])
@requires_auth(permission="get:drinks-detail")
def get_drinks_detail():
    drinks = Drink.query.all()
    long_drinks = [drink.long() for drink in drinks]

    if not drinks:
        abort(400)
    
    return jsonify({
        "success": True,
        "drinks": long_drinks
    })


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth(permission="post:drinks")
def new_drink():
    data = request.get_json()

    if not data:
        abort(404)

    title = data.get("title")
    recipe = data.get("recipe")

    drink = Drink(
            title=title,
            recipe=recipe
        )

    try:
       drink.insert()
       return jsonify({
        "success": True,
        "drink": drink.long()
       })

    except Exception as e:
        print(e)
        abort(500)

   


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<drink_id>", methods=["PATCH"])
@requires_auth(permission="patch:drinks")
def edit_drink(drink_id):
    drink = Drink.query.get(drink_id)
    data = request.get_json()

    recipe = data.get("recipe")

    if not drink:
        abort(404)

    drink.title = data.get("title")
    drink.recipe = recipe if type(recipe) == str else json.dumps(recipe)

    try:
        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception as e:
        print(e)
        abort(500)

    


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<drink_id>", methods=["DELETE"])
@requires_auth(permission="delete:drinks")
def delete_drink(drink_id):
    drink = Drink.query.get(drink_id)

    if not drink:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        })
    except Exception as e:
        print(e)
        abort(500)



# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "Resource not found",
        "error": "404"
    }), 404

'''
@DONE implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "message": "internal server error",
        "error": 500
    }), 500

'''
@DONE implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "message": "Authentication Error",
        "error": AuthError(error)
    })