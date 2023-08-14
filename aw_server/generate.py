import jwt
import rsa
from datetime import datetime, timedelta

class TokenGenerator:
    def __init__(self):
        secretKey =  b'\t\xfc,\x1d\xe8>\xbcz\xa41\xf7\xf9\xf3\xcf\xd2\x19\xd0{cm?\xd5\xb8\xdf\xb8\xd0r\'\xc0\x115\xfd\x0c?0X\x83.`S\x9b\xe3\x97\xc2\xf5\x01\r"\xf6:~>\xd5q\xa7\xc1\xb0x^\xe7O\x0bJ\xfe'
        
        privateKey = (6802324025186300087345894824872359628138496789147567568361215883209761267907618833673302338965569519619192605653295381471129865156946317474747627659265851, 65537, 5718718385273808320681397793093861458894162955149969182507559264494990864268844596934801512532241816917162193129891973655273062735658177588093511880455625, 5559627683216318273807037909647988039464950410376515463146335584710167553473681837, 1223521504096667407649842992034512089495877071257451214377174507855122823)
        tesKey = rsa.PrivateKey(*privateKey)

        decMessage = rsa.decrypt(secretKey, tesKey).decode()

        self.secret_key = decMessage


    def generate_token(self, username):
        #username_valid = self.validate_username(username)
        expiration_days=7
        payload = {
            "username": username,
            "exp": datetime.utcnow() + timedelta(days=expiration_days)
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")

        return token
    
    
token_generator = TokenGenerator()  
    