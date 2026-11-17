import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder='uploads'):
    """
    Save uploaded file to the specified folder
    Returns the file path if successful, None otherwise
    """
    if file and file.filename and allowed_file(file.filename):
        # Get file extension
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.{file_ext}"
        
        # Get base directory - use the same method as main.py
        # current_app.root_path points to where Flask app is initialized
        # For our structure, we need the directory containing main.py
        # If app structure is: backend/main.py and backend/app/, 
        # root_path might be backend/ or backend/app/
        
        # Get the directory where the Flask app's root is
        app_root = current_app.root_path
        
        # If root_path ends with 'app', go up one level to get backend directory
        if app_root.endswith('app') or os.path.basename(app_root) == 'app':
            base_dir = os.path.dirname(app_root)
        else:
            # Otherwise, root_path should be the backend directory
            base_dir = app_root
        
        upload_folder = os.path.join(base_dir, folder)
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Verify file was saved
        if not os.path.exists(file_path):
            print(f"Error: File was not saved at {file_path}")
            print(f"Attempted to save to: {file_path}")
            print(f"Base directory: {base_dir}")
            print(f"Upload folder: {upload_folder}")
            print(f"App root path: {current_app.root_path}")
            return None
        
        # Debug: Print where file was saved (remove in production)
        print(f"File saved successfully: {file_path}")
        print(f"Relative path returned: {folder}/{filename}")
        
        # Return relative path for database storage
        return f"{folder}/{filename}"
    return None

def delete_file(file_path):
    """Delete a file from the filesystem"""
    try:
        if file_path:
            full_path = os.path.join(current_app.root_path, '..', file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
    except Exception as e:
        print(f"Error deleting file: {e}")
    return False

