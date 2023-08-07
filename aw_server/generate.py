import jwt
from datetime import datetime, timedelta

class TokenGenerator:
    def __init__(self):
        self.secret_key = "M4nd1r1"

    def generate_token(self, username):
        #username_valid = self.validate_username(username)
        expiration_days=7
        payload = {
            "username": username,
            "exp": datetime.utcnow() + timedelta(days=expiration_days)
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")

        return token
    
    
  
    