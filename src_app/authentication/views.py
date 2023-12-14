from flask import Blueprint, request, jsonify, make_response
from src_app.authentication.models import User, db
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os



authentication_bp = Blueprint("authentication", __name__)


@authentication_bp.route("/")
def home():
    return "hello world!"

#decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        #returning 401 if token is not passed
        if not token:
            return jsonify({"message":"Token is missing!!"}), 401
        try:
            #decoding the payload to fetch the stored details
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except Exception as e:
            print(e)
            return jsonify({"message": 'Token is invalid!!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

@authentication_bp.route("/user", methods=['GET'])
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    users = User.query.all()
    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        output.append({
            'public_id':user.public_id,
            'name':user.name,
            'email':user.email
        })

    return jsonify({'users':output})

# route for logging user in
@authentication_bp.route('/login', methods=['POST'])
def login():
    #create dictionary of form data
    auth = request.form
    email = auth.get('email')
    password = auth.get('password')
    print(email, password)
    if not auth or not auth.get('email') or not auth.get('password'):
        #return 401 if any email or password is missing
        return make_response('Could not verify',401,
                             {'WWW-Authenticate':'Basic realm = "Login required!!"'})

    user = User.query.filter_by(email=auth.get('email')).first()

    if not user:
        #returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401, {'WWW-Authenticate':'Basic realm="User does not exist!!"'}
        )
    if check_password_hash(user.password, auth.get('password')):
        #generate the JWT token
        token = jwt.encode({
            'public_id':user.public_id,
            'exp':datetime.utcnow()+timedelta(minutes=30)
        }, os.getenv('SECRET_KEY'), algorithm='HS256')
        return make_response(jsonify({'token':token}), 201)
    #return 403 if password is wrong
    return make_response(
        'Could not verify',403,{'WWW-Authenticate':'Basic realm="Wrong password!!"'}
    )

#signup
@authentication_bp.route("/signup", methods=['POST'])
def signup():
    #create dictionary of the form data
    data = request.form


    #gets name, email and password
    name, email = data.get('name'), data.get('email')
    password = data.get('password')
    print(name,email,password)

    #checking for existing user
    user = User.query.filter_by(email=email).first()
    if not user:
        #database ORM object
        user = User(name, email, password)
        #insert user
        db.session.add(user)
        db.session.commit()

        return make_response('Successfully registered.', 201)
    else:
        #return 202 if user already exists
        return make_response('User already exists. please log in', 202)