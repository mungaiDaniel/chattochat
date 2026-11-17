from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_cors import CORS
import os
from database.database import MY_DATABASE
from config import DevelopmentConfig
from app.users.routes import user_v1
from app.posts.routes import post_v1
from app.comments.routes import comment_v1
from app.follow.route import follow_v1



app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config.from_object(DevelopmentConfig)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=1)
JWTManager(app)

# Create uploads directory if it doesn't exist
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(os.path.join(uploads_dir, 'photos'), exist_ok=True)
os.makedirs(os.path.join(uploads_dir, 'posts'), exist_ok=True)

# Route to serve uploaded images (handles subdirectories)
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded images from uploads directory and subdirectories"""
    try:
        # filename will be like "photos/filename.jpg" or "posts/filename.jpg" or just "filename.jpg"
        # Build the full path
        file_path = os.path.join(uploads_dir, filename)
        
        # Check if file exists
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # If it's in a subdirectory, extract directory and filename
            if '/' in filename:
                directory = os.path.join(uploads_dir, os.path.dirname(filename))
                file_name = os.path.basename(filename)
                response = send_from_directory(directory, file_name)
            else:
                response = send_from_directory(uploads_dir, filename)
            
            # Add CORS headers
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'GET')
            return response
        else:
            # File not found - log for debugging
            print(f"File not found: {file_path}")
            print(f"Uploads directory: {uploads_dir}")
            print(f"Requested filename: {filename}")
            from flask import abort
            abort(404)
    except Exception as e:
        from flask import abort
        print(f"Error serving file {filename}: {e}")
        print(f"Uploads directory: {uploads_dir}")
        import traceback
        traceback.print_exc()
        abort(404)

app.register_blueprint(user_v1)
app.register_blueprint(post_v1)
app.register_blueprint(comment_v1)
app.register_blueprint(follow_v1)

MY_DATABASE.connect_to_db()
MY_DATABASE.create_user_table()
MY_DATABASE.create_follows_table()
MY_DATABASE.create_post_table()
MY_DATABASE.create_comments_table()
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)



