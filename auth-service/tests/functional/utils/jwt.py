import jwt


def get_user_from_token(token: str):
    return jwt.decode(token, options={'verify_signature': False})['sub']


def get_perm_from_token(token: str):
    return jwt.decode(token, options={'verify_signature': False})['perm']
