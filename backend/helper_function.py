import json

def register_user(self):
    '''register user'''
    new_user = {
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "Sincere@april.biz",
        "password": "password123",
        "user_role": "user"
    }
    return self.client.post(
        'api/v1/register',
        data=json.dumps(new_user),
        content_type='application/json'
    )

def register_user2(self):
    '''register user'''
    return self.client.post(
        'api/v1/register',
        data=json.dumps(dict(
            name="name22", 
            username="username222", 
            email="email22@com", 
            password="password123",
            user_role="user"
        )),
        content_type='application/json'
    )
    
def login_user(self):
    '''login the registered user'''
    return self.client.post(
        'api/v1/login',
        data=json.dumps(dict(
            username="Bret",
            password="password123"
        )),
        content_type='application/json'
    )
    
def post_posts(self):
    
    response = login_user(self)
    result = json.loads(response.data)
    self.assertIn("token", result)
    new_post = {'user_id': 1, 'title': 'error sit voluptatem accusantium doloremque laudantium',
                    'body': 'error sit voluptatem accusantium doloremque laudantiumerror sit volupta'}
    response = self.client.post('api/v1/post', data=json.dumps(new_post),
                                headers={'Authorization': f'Bearer {result["token"]}',
                                         'Content-Type': 'application' '/json'})
    return response

def post_comments(self):
    
    response = login_user(self)
    result = json.loads(response.data)
    self.assertIn("token", result)
    new_comment = {"name":" kndwjwdjsnksia ",  'body': 'errossssssssssssssssssssssssssssssssssssssssssssssssss'}
    response = self.client.post('/api/v1/comment/1', data=json.dumps(new_comment),
                                    headers={'Authorization': f'Bearer {result["token"]}',
                                             'Content-Type': 'application' '/json'})
    return response