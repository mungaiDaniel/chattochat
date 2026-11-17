# Backend Updates Required for Profile Picture Upload

## Overview
The frontend now uploads photos and saves the profile picture URL to the user's profile. You need to create a backend endpoint to update user profile information.

## Required Backend Endpoint

### PUT /api/v1/user/profile

**Purpose:** Update the current user's profile information (profile picture, cover picture, etc.)

**Authentication:** Required (Bearer token in Authorization header)

**Request Body (JSON):**
```json
{
  "personPic": "filename.jpg",     // For profile picture
  "coverPic": "cover.jpg"           // For cover picture
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "name": "User Name",
    "username": "username",
    "email": "user@example.com",
    "personPic": "filename.jpg",
    "coverPic": "cover.jpg",
    // ... other user fields
  }
}
```

**Response (Error - 400/401/500):**
```json
{
  "success": false,
  "message": "Error message here"
}
```

## Implementation Details

### What the Frontend Does:
1. Uploads photo file to `/api/v1/upload-photo` (already exists)
2. Gets filename from upload response
3. Calls `PUT /api/v1/user/profile` with the filename
4. Refreshes user data to display updated profile

### What Your Backend Should Do:
1. Extract user ID from JWT token
2. Validate the request body
3. Update the user record in database with:
   - `personPic` field (for profile picture)
   - `coverPic` field (for cover picture)
4. Return updated user data

## Example Backend Implementation (Python/Flask)

```python
@app.route('/api/v1/user/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    try:
        # Get current user from token
        current_user_id = get_jwt_identity()
        
        # Get request data
        data = request.get_json()
        
        # Update user profile
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        
        # Update fields if provided
        if 'personPic' in data:
            user.personPic = data['personPic']
        if 'coverPic' in data:
            user.coverPic = data['coverPic']
        
        # Save to database
        db.session.commit()
        
        # Return updated user
        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "data": {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "email": user.email,
                "personPic": user.personPic,
                "coverPic": user.coverPic,
                # ... other fields
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
```

## Database Schema Requirements

Make sure your user table has these fields:
- `personPic` (VARCHAR/TEXT) - stores the filename of profile picture
- `coverPic` (VARCHAR/TEXT) - stores the filename of cover picture

## Notes

- The frontend sends just the filename (e.g., "photo123.jpg"), not the full URL
- The full URL is constructed on the frontend as: `http://127.0.0.1:5000/uploads/{filename}`
- Make sure your `/api/v1/user` GET endpoint returns these fields so the frontend can display them
- The endpoint should only allow users to update their own profile (check JWT token)

## Testing

After implementing, test with:
```bash
curl -X PUT http://127.0.0.1:5000/api/v1/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"personPic": "test.jpg"}'
```

