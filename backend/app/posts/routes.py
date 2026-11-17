from flask import Blueprint, make_response, jsonify, request, current_app
from app.posts.model import PostModel
from app.users.model import UserModel
import datetime
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.file_upload import save_uploaded_file


post_v1 = Blueprint("post_v1", __name__, url_prefix='/api/v1')

@post_v1.route('/post', methods=['POST'])
@jwt_required()
def post():
    try:
        user_id = get_jwt_identity()
        
        # Check if request contains file upload
        if 'photo' in request.files:
            file = request.files['photo']
            postpic = save_uploaded_file(file, folder='uploads/posts')
            if not postpic:
                return make_response(jsonify({
                    "status": 400,
                    "message": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp"
                }), 400)
        else:
            # Fallback to JSON data if no file upload
            data = request.get_json() or {}
            postpic = data.get('postpic', '')
        
        # Get other post data from form or JSON
        body = request.form.get('body') or (request.get_json() or {}).get('body', '')
        likes = int(request.form.get('likes', 0) or (request.get_json() or {}).get('likes', 0))
        
        if not body:
            return make_response(jsonify({
                "status": 400,
                "message": "Post body is required"
            }), 400)
        
        new_post = PostModel(id=None, user_id=user_id, postpic=postpic, likes=likes, body=body, date_created=datetime.datetime.now())
        new_post.save(user_id=user_id, postpic=postpic, likes=likes, body=body, date_created=datetime.datetime.now())

        return make_response(jsonify({
            "status": 201,
            "data": new_post.json_dumps(),
            "msg": "posted successfully"
        }), 201)
    except Exception as e:
        return make_response(jsonify({
            "status": 500,
            "message": str(e)
        }), 500)

@post_v1.route('/post', methods=['GET'])
def get_all_post():
    posts = PostModel.get_all()

    return make_response(jsonify({
        "status":200,
        "data": posts
    }), 200)

@post_v1.route('/post/<int:id>', methods=['GET'])
def get_on(id):

    post = PostModel.get_by_id(id=id)

    if post:
        return make_response(jsonify({
            "status": 200,
            "data": post
        }), 200)
    return make_response(jsonify({
        "status": 404,
        "data": "No Post Found By That ID"
    }), 404)

@post_v1.route('/mypost', methods=['GET'])
@jwt_required()
def get_mypost():

    user = get_jwt_identity()

    posts = PostModel.get_all_user_post(user)

    return make_response(jsonify({
        "status":200,
        "data": posts
    }), 200)

@post_v1.route('/post20', methods=['GET'])
def get_20_post():
    posts = PostModel.get_20_post()

    return make_response(jsonify({
        "status":200,
        "data": posts
    }), 200)

