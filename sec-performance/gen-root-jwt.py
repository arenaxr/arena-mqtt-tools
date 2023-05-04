import jwt
from datetime import datetime, timedelta

def generate_token(username, keypath, sub_topics=['#'], pub_topics=['#']):
    now = datetime.utcnow()
    claim = {
        "sub": username,
        "subs": sub_topics,
        "publ": pub_topics,
        'iat': now,
        'exp': now + timedelta(days=365)
    }
    with open(keypath, 'r') as keyfile:
        key = keyfile.read()
    token = jwt.encode(claim, key, algorithm='RS256')
    return {
        "username": username,
        "token": token
    }

def main():
    creds = generate_token('cli', './keys/jwt.priv-arena0.pem', sub_topics=['#'], pub_topics=['#'])
    
    print(creds)
    
if __name__ == "__main__":
    main()    