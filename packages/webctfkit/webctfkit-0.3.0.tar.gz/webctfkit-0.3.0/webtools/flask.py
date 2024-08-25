from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer

def generate_session(session_data, secret_key):
    serializer = URLSafeTimedSerializer(secret_key)
    session_interface = SecureCookieSessionInterface()
    session_cookie = session_interface.get_signing_serializer(serializer).dumps(session_data)

    return session_cookie
