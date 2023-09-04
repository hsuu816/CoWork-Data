import bcrypt
import json
import time
from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from server import app
from server.models.user_model import get_user, create_user
from server.models.tracking_model import get_user_behavior_by_date, create_user_event
from server.utils.util import dir_last_updated

TOKEN_EXPIRE = app.config['TOKEN_EXPIRE']

def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf8'), bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf8'), hashed_password.encode('utf8'))

@app.route('/signin', methods=['GET'])
def signin_page():
    return render_template('signin.html', last_updated=dir_last_updated('server/static'))

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html', last_updated=dir_last_updated('server/static'))

@app.route('/profile', methods=['GET'])
def profile_page():
    return render_template('profile.html', last_updated=dir_last_updated('server/static'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', last_updated=dir_last_updated('server/static'))

@app.route('/api/1.0/signin', methods=['POST'])
def api_signin():
    form = request.form.to_dict()
    email = form.get('email', None) 
    password = form.get('password', None)

    user = get_user(email)
    if not user:
        return jsonify({"error": "Bad username"}), 401

    if not check_password(password, user["password"]):
        return jsonify({"error": "Bad password"}), 401

    access_token = create_access_token(identity=user["username"])
    return {
        "access_token": access_token,
        "access_expired": TOKEN_EXPIRE,
        "user": {
            "id": user["id"],
            "provider": 'native',
            "name": user["username"],
            "email": email,
            "picture": ""
        }
    }

@app.route('/api/1.0/signup', methods=['POST'])
def api_signup():
    form = request.form.to_dict()
    name = form.get('name', None)
    email = form.get('email', None) 
    password = form.get('password', None)
    encrypted_password = get_hashed_password(password)
    user = get_user(email)
    if user:
        return jsonify({"error": "User already existed"}), 401
    access_token = create_access_token(identity=name)
    user_id = create_user({
        "provider": 'native',
        "email": email,
        "password": encrypted_password,
        "name": name,
        "picture": None,
        "access_token": access_token,
        "access_expired": TOKEN_EXPIRE
    })
    return {
        "access_token": access_token,
        "access_expired": TOKEN_EXPIRE,
        "user": {
            "id": user_id,
            "rovider": 'native',
            "name": name,
            "email": email,
            "picture": ""
        }
    }

@app.route('/api/1.0/profile', methods=['GET'])
@jwt_required
def api_get_user_profile():
    current_user = get_jwt_identity()
    return f"Welcome! {current_user}"

@app.route('/api/1.0/user/behavior/<date>')
def api_get_user_behavior(date):
    data = get_user_behavior_by_date(date)
    if (data):
        return {
            "behavior_count": [data['view_count'], data['view_item_count'], data['add_to_cart_count'], data['checkout_count']],
            "user_count": [data['all_user_count'], data['active_user_count'], data['new_user_count'], data['return_user_count']]
        }
    else:
        return {
            "behavior_count": [0]*4,
            "user_count": [0]*4
        }

@app.route('/api/1.0/user/event', methods=['POST'])
def get_user_event():
    try:
        data = request.data
        data_str = data.decode('utf-8')
        json_data = json.loads(data_str)

        event = {
            'system': json_data['system'],
            'version': json_data['version'],
            'category': json_data['category'],
            'event': json_data['event'],
            'event_detail': json_data['event_detail'],
            'user_email': json_data['user_email'],
            'user_id': json_data['user_id'],
            'created_time': int(time.time() * 1000)
        }

        valid_events = ["view_item", "add_to_cart", "checkout"]
        category = ["hot", "all", "men", "women", "accessories", "checkout"]

        if event['event'] not in valid_events:
            response = {"status": f"Invalid event. Supported events are <{', '.join(valid_events)}>."}
        elif event['category'] not in category:
            response = {"status": f"Invalid category. Supported categories are <{', '.join(category)}>."}
        else:
            create_user_event(event)
            response = {"status": "OK"}

    except Exception as e:
        response = {"status": f"Error: {str(e)}"}

    return response
