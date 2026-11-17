from datetime import datetime
import datetime
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, create_access_token
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from database.database import MY_DATABASE


cursor = MY_DATABASE.connect_to_db()

class UserModel(MY_DATABASE):
    def __init__(self, id, name, username, email, password, user_role, date_created, personPic=None, coverPic=None):
        self.id = id
        self.name = name
        self.username = username
        self.email = email
        self.password = password
        self.user_role = user_role
        self.personPic = personPic
        self.coverPic = coverPic
        self.date_created = date_created

    

    def save(self, name, username, email, password, user_role, date_created):
        format_str = f"""
                 INSERT INTO public.user (name, username, email, password, user_role, date_created)
                 VALUES ('{name}', '{username}', '{email}', '{password}', '{user_role}', '{str(datetime.datetime.now().date())}')

                 """
        cursor.execute(format_str)
        return {
            "name": name, 
            "username": username, 
            "email": email, 
            "user_role": user_role, 
            "date_created": str(date_created)
        }

    def generate_auth_token(self, permission_level):

    
        if permission_level == 1:

            token = create_access_token(identity=self.id, additional_claims={'admin': 1})

            return token

        return create_access_token(identity=self.id, additional_claims={'admin': 0})

    @staticmethod
    def generate_hash(password):
        '''method that returns a hash'''
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        '''method to verify password with the hash'''
        return pbkdf2_sha256.verify(password, hash)
    
    def json_dumps(self):
        '''method to return a json object from a user'''
        # Convert file paths to URLs if they exist
        personPic_url = None
        coverPic_url = None
        
        if self.personPic:
            if self.personPic.startswith('uploads/'):
                personPic_url = f"/{self.personPic}"
            else:
                personPic_url = self.personPic
        
        if self.coverPic:
            if self.coverPic.startswith('uploads/'):
                coverPic_url = f"/{self.coverPic}"
            else:
                coverPic_url = self.coverPic
        
        ans = { 
            "id": self.id,
            "name": self.name, 
            "username": self.username, 
            "email": self.email, 
            "user_role": self.user_role,
            "personPic": personPic_url,
            "coverPic": coverPic_url,
            "date_created": str(self.date_created) 
        }
        return ans
    
    @classmethod
    def find_by_email(cls, email):
        '''This method gets a user using email'''
        try:
            format_str = f"""SELECT * FROM \"user\" WHERE email = '{email}' 
                        """
            cursor.execute(format_str)
            user = cursor.fetchone()
            if user:
                return list(user)
            return None
        except Exception as e:
            return {'error': e}

    @classmethod
    def find_by_username(cls, username):
        '''method to find a user by username'''
        try:
            format_str = f"""SELECT * FROM \"user\" WHERE username = '{username}'  LIMIT 1
                        """
            cursor.execute(format_str)
            user = cursor.fetchone()
            if user:
                return list(user)
            return None
        except Exception as e:
            print('::::::', e)
            return {'error': e}

    @classmethod
    def find_by_id(cls, id):
        '''method to find a user by id'''
        try:
            format_str = f"""SELECT * FROM \"user\" WHERE id = {id}  LIMIT 1
                        """
            cursor.execute(format_str)
            retrieved_user = list(cursor.fetchone())
            # Handle cases where personPic and coverPic might be None or at different indices
            personPic = retrieved_user[7] if len(retrieved_user) > 7 else None
            coverPic = retrieved_user[8] if len(retrieved_user) > 8 else None
            user = UserModel(
                id=retrieved_user[0], 
                name=retrieved_user[1], 
                username=retrieved_user[2], 
                email=retrieved_user[3], 
                password=retrieved_user[4], 
                user_role=retrieved_user[5], 
                date_created=retrieved_user[6],
                personPic=personPic,
                coverPic=coverPic
            )

            return user.json_dumps()
        except Exception as e:
            return {"error": e}
        
    @classmethod
    def find_email(cls, id):
        '''method to find am email'''
        try:
            format_str = f"""SELECT * FROM public.user WHERE id = {id}  LIMIT 1
                        """
            cursor.execute(format_str)
            retrieved_user = list(cursor.fetchone())
            personPic = retrieved_user[7] if len(retrieved_user) > 7 else None
            coverPic = retrieved_user[8] if len(retrieved_user) > 8 else None
            user = UserModel(
                id=retrieved_user[0], 
                name=retrieved_user[1], 
                username=retrieved_user[2], 
                email=retrieved_user[3], 
                password=retrieved_user[4], 
                user_role=retrieved_user[5], 
                date_created=retrieved_user[6],
                personPic=personPic,
                coverPic=coverPic
            )

            return user.email
        except Exception as e:
            return {"error": e}
        
    @classmethod
    def get_id(cls, id):
        '''method to find a user by id'''
        try:
            format_str = f"""SELECT * FROM \"user\" WHERE id = {id}  LIMIT 1
                        """
            cursor.execute(format_str)
            retrieved_user = list(cursor.fetchone())
            personPic = retrieved_user[7] if len(retrieved_user) > 7 else None
            coverPic = retrieved_user[8] if len(retrieved_user) > 8 else None
            user = UserModel(
                id=retrieved_user[0], 
                name=retrieved_user[1], 
                username=retrieved_user[2], 
                email=retrieved_user[3], 
                password=retrieved_user[4], 
                user_role=retrieved_user[5], 
                date_created=retrieved_user[6],
                personPic=personPic,
                coverPic=coverPic
            )

            return user.id
        except Exception as e:
            return {"error": e}
        
    @classmethod
    def get_all(cls):
        
        ''' method to get all users'''
        cursor.execute(
            f"SELECT * FROM public.user"
        )
        rows = cursor.fetchall()
        
        output = []
        
        for row in rows:
            personPic = row[7] if len(row) > 7 else None
            coverPic = row[8] if len(row) > 8 else None
            new = UserModel(
                id=row[0], 
                name=row[1], 
                username=row[2], 
                email=row[3], 
                password=row[4], 
                user_role=row[5], 
                date_created=row[6],
                personPic=personPic,
                coverPic=coverPic
            )
            
            output.append(new.json_dumps())
            
        return output
    
    @classmethod
    def update(cls, user_role, id):
        """Method to update an user_role"""
        format_str = f"""
         UPDATE public.user SET user_role = '{user_role}' WHERE id = {id};
         """

        cursor.execute(format_str)

        return {
            "user_role": user_role
        }
    
    @classmethod
    def update_profile(cls, id, personPic=None, coverPic=None):
        """Method to update user profile pictures"""
        try:
            updates = []
            values = []
            
            if personPic is not None:
                updates.append("personPic = %s")
                values.append(personPic)
            
            if coverPic is not None:
                updates.append("coverPic = %s")
                values.append(coverPic)
            
            if not updates:
                return {"error": "No fields to update"}
            
            values.append(id)
            format_str = f"""
                UPDATE public.user 
                SET {', '.join(updates)}
                WHERE id = %s
            """
            
            cursor.execute(format_str, tuple(values))
            
            # Return updated user
            updated_user = cls.find_by_id(id)
            return updated_user
            
        except Exception as e:
            return {"error": str(e)}
        