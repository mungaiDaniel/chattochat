import os
import psycopg2

class MY_DATABASE:

    def connect_to_db():

        connect = psycopg2.connect(os.environ['DATABASE_URL'])
        connect.autocommit = True
        cursor = connect.cursor()
        return cursor

    def create_user_table():

        cursor = MY_DATABASE.connect_to_db()
        sql_command = """CREATE TABLE IF NOT EXISTS "public"."user"(
        id SERIAL,
        name VARCHAR(100),
        username VARCHAR(500) NOT NULL,
        email VARCHAR(100) UNIQUE,
        password VARCHAR(500),
        user_role VARCHAR(200) DEFAULT 'user',
        personPic VARCHAR(500),
        coverPic VARCHAR(500),
        date_created VARCHAR(80),
        PRIMARY KEY (id)
        

        )"""
        cursor.execute(sql_command)
        
        # Add personPic and coverPic columns if they don't exist (for existing databases)
        # Try to add columns and silently ignore if they already exist
        try:
            cursor.execute("""
                ALTER TABLE "public"."user" 
                ADD COLUMN "personPic" VARCHAR(500);
            """)
        except Exception as e:
            # Column already exists - ignore silently
            # Check if error is about duplicate column
            error_msg = str(e).lower()
            if 'already exists' not in error_msg and 'duplicate' not in error_msg:
                # Only print if it's a different error
                print(f"Warning adding personPic column: {e}")
        
        try:
            cursor.execute("""
                ALTER TABLE "public"."user" 
                ADD COLUMN "coverPic" VARCHAR(500);
            """)
        except Exception as e:
            # Column already exists - ignore silently
            # Check if error is about duplicate column
            error_msg = str(e).lower()
            if 'already exists' not in error_msg and 'duplicate' not in error_msg:
                # Only print if it's a different error
                print(f"Warning adding coverPic column: {e}")

    def create_post_table():

        cursor = MY_DATABASE.connect_to_db()
        sql_command = """CREATE TABLE IF NOT EXISTS "public"."post"(
        id SERIAL,
        user_id INTEGER NOT NULL,
        postpic VARCHAR(200),
        likes INTEGER,
        body VARCHAR(500),
        date_created VARCHAR(80),
        PRIMARY KEY (id),
        FOREIGN KEY (user_id)
        REFERENCES \"user\" (id)
        

        )"""
        cursor.execute(sql_command)

    def create_comments_table():

        cursor = MY_DATABASE.connect_to_db()
        sql_command = """ CREATE TABLE IF NOT EXISTS "public"."comment"  (
                id SERIAL ,
                body VARCHAR(400) NOT NULL,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                email VARCHAR(50), 
                date_created VARCHAR(80),
                PRIMARY KEY (id),
                FOREIGN KEY (post_id)
                REFERENCES \"post\" (id),
                FOREIGN KEY (user_id)
                REFERENCES \"user\" (id)
                    )"""
        cursor.execute(sql_command)

    def create_follows_table():

        cursor = MY_DATABASE.connect_to_db()
        sql_command = """ CREATE TABLE IF NOT EXISTS "public"."follow"(
        
                id SERIAL PRIMARY KEY,
                follower_id INTEGER NOT NULL,
                followee_id INTEGER NOT NULL,
                FOREIGN KEY (follower_id) REFERENCES \"user\" (id),
                FOREIGN KEY (followee_id) REFERENCES \"user\" (id)         
        )  

        """
        cursor.execute(sql_command)


    def drop_post_table():
        '''function to drop post table'''
        cursor = MY_DATABASE.connect_to_db()
        sql_command = """ DROP TABLE \"post\" CASCADE;"""
        cursor.execute(sql_command)


    def drop_comment_table():
        '''function to drop comment table'''
        cursor =MY_DATABASE.connect_to_db()
        sql_command = """ DROP TABLE \"comment\" CASCADE;"""
        cursor.execute(sql_command)


    def drop_users_table():
        '''function to drop user table'''
        cursor =MY_DATABASE.connect_to_db()
        sql_command = """ DROP TABLE \"user\" CASCADE;"""
        cursor.execute(sql_command)

    def drop_follow_table():
        cursor =MY_DATABASE.connect_to_db()
        sql_command = """ DROP TABLE \"follow\" CASCADE;"""
        cursor.execute(sql_command)

