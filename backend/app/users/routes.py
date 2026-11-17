from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import Blueprint, make_response, jsonify, request
from app.users.model import UserModel
from flask_cors import cross_origin
import datetime
from utils.file_upload import save_uploaded_file

user_v1 = Blueprint('user-v1', __name__, url_prefix='/api/v1')

@user_v1.route('/register', methods=['POST'])
def post():
    try:
        data = request.get_json()

        name = data['name']
        username = data['username']
        email = data['email']
        password = UserModel.generate_hash(data['password'])
        user_role = data.get('user_role', 'user')
        date_created = datetime.datetime.now()

        # Check if username already exists
        existing_user = UserModel.find_by_username(username)
        if existing_user and not isinstance(existing_user, dict):
            return make_response(jsonify({
                "status": 409,
                "message": "This username is already taken, kindly try another username"
            }), 409)

        new_user = UserModel(id=None, name=name, username=username, email=email, password=password, user_role=user_role, date_created=date_created)

        new_user.save(name=name, username=username, email=email, password=password, user_role=user_role, date_created=date_created)

        return make_response(jsonify({ 
            "status": 201,
            "data": new_user.json_dumps()
        }), 201)
    except KeyError as e:
        return make_response(jsonify({
            "status": 400,
            "message": f"Missing required field: {str(e)}"
        }), 400)
    except Exception as e:
        return make_response(jsonify({
            "status": 500,
            "message": str(e)
        }), 500)

@user_v1.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'username {} doesnt exist'.format(data['username'])}, 404

        password = data['password']
        hash = current_user[4]  # password is at index 4 (id=0, name=1, username=2, email=3, password=4, user_role=5, date_created=6, personPic=7, coverPic=8)

        if not UserModel.verify_hash(password, hash):
            return {"message": "Incorrect password"}, 401
        
        personPic = current_user[7] if len(current_user) > 7 else None
        coverPic = current_user[8] if len(current_user) > 8 else None
        user = UserModel(
            id=current_user[0], 
            name=current_user[1], 
            username=current_user[2], 
            email=current_user[3], 
            password=current_user[4], 
            user_role=current_user[5], 
            date_created=current_user[6],
            personPic=personPic,
            coverPic=coverPic
        )

        if user.user_role == 'premium':
            permission_level = 1
        else:
            permission_level = 0

        token = user.generate_auth_token(permission_level)

        return jsonify({'token': token, "user_role": user.user_role, "id": user.id}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@user_v1.route('/user', methods=['GET'])
def get_all_users():
    users = UserModel.get_all()

    return make_response(jsonify({
        "status": 200,
        "data": users
    }), 200)

@user_v1.route('/user/<int:id>', methods=['GET'])
def get_one_user(id):
    user = UserModel.find_by_id(id)

    return make_response(jsonify({
        "status": 200,
        "data": user
    }), 200)

@user_v1.route('/premium', methods=['PUT'])
@jwt_required()
def update_tO_premium():
    user_role = request.get_json()

    user_id = get_jwt_identity()

    user = UserModel.update(user_role=user_role['user_role'] , id=user_id)

    return make_response(jsonify({
        "status": 200,
        "data": user
    }), 200)

@user_v1.route('/upload-photo', methods=['POST'])
@jwt_required()
def upload_photo():
    """Upload a photo and return the file path"""
    try:
        if 'photo' not in request.files:
            return make_response(jsonify({
                "status": 400,
                "message": "No file provided. Please use 'photo' as the field name."
            }), 400)
        
        file = request.files['photo']
        
        if file.filename == '':
            return make_response(jsonify({
                "status": 400,
                "message": "No file selected"
            }), 400)
        
        # Save file to uploads/photos folder
        file_path = save_uploaded_file(file, folder='uploads/photos')
        
        if not file_path:
            return make_response(jsonify({
                "status": 400,
                "message": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp"
            }), 400)
        
        # Return the URL path that can be used to access the image
        # file_path is like "uploads/photos/filename.jpg"
        # The URL should be "/uploads/photos/filename.jpg"
        photo_url = f"/{file_path}"
        
        return make_response(jsonify({
            "status": 200,
            "message": "Photo uploaded successfully",
            "file_path": file_path,
            "photo_url": photo_url
        }), 200)
        
    except Exception as e:
        return make_response(jsonify({
            "status": 500,
            "message": str(e)
        }), 500)

@user_v1.route('/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile with personPic and/or coverPic filenames"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return make_response(jsonify({
                "status": 400,
                "message": "No data provided"
            }), 400)
        
        personPic = data.get('personPic')
        coverPic = data.get('coverPic')
        
        # At least one field must be provided
        if personPic is None and coverPic is None:
            return make_response(jsonify({
                "status": 400,
                "message": "At least one field (personPic or coverPic) must be provided"
            }), 400)
        
        # Update user profile
        updated_user = UserModel.update_profile(
            id=user_id,
            personPic=personPic,
            coverPic=coverPic
        )
        
        if 'error' in updated_user:
            return make_response(jsonify({
                "status": 500,
                "message": updated_user['error']
            }), 500)
        
        return make_response(jsonify({
            "status": 200,
            "message": "Profile updated successfully",
            "data": updated_user
        }), 200)
        
    except Exception as e:
        return make_response(jsonify({
            "status": 500,
            "message": str(e)
        }), 500)


    
      


            


