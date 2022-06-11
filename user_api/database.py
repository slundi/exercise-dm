import os
import psycopg2

conn = psycopg2.connect(host="db", database=os.getenv("POSTGRES_DB"), user="postgres", password=os.getenv("POSTGRES_PASSWORD"))
cur = conn.cursor()

class WrongActivationCodeException(Exception):
    """ Raised exception when we try to match a wrong activation code (example: using one from deprecated email) """

class ExpiredActivationCodeException(Exception):
    """ Raised exception when we try to activate an expired code """

def get_user(email: str):
    """ Get user from the email.
    We return the all the user info.
    Password check is not performed with the database because BCrypt is not available
    """
    cur.execute('SELECT * FROM users WHERE email=%(email)s', {'email': email})
    return cur.fetchone()

def auth(user_id: int, token: str, host: str):
    """ Store the auth token.
    It also clean expired tokens for the user
    """
    cur.execute('DELETE FROM auth_tokens WHERE user_id=%(id)i AND EXTRACT(EPOCH FROM (expires - CURRENT_TIMESTAMP)) > %(delay)i', {'id': user_id, 'delay': os.getenv('TOKEN_DELAY', 600)})
    cur.execute("""INSERT INTO auth_tokens(user_id, token, expires)
                  VALUES(%(id)i, %(token)s, CURRENT_TIMESTAMP + %(delay)i * interval '1 second')
                  """, {'id': user_id, 'token': token, 'delay': os.getenv('TOKEN_DELAY', 600)})
    last_id = cur.fetchone()[0]
    cur.commit()
    cur.execute('SELECT * FROM auth_tokens WHERE user_id=%(user)i AND id=%(id)i', {'id': last_id, 'user': user_id})
    return cur.fetchone()


def create_user(email: str, hashed_password: str):
    """ Create the user in the database from the email and the hashed password """
    cur.execute('INSERT INTO users(email, psw) VALUES(%(email)s)', {'email': email})
    cur.commit()

def get_activation(email: str):
    """ Get activation information (email, activation code, expire date UTC, remaining time before expiration) from user's email.
    If user's activation is expired, it returns None
    """
    cur.execute("""SELECT email, code, expires, EXTRACT(EPOCH FROM (expires - CURRENT_TIMESTAMP)) remaining_time
                  FROM activation_codes INNER JOIN users ON users.id = user_id
                  WHERE email=%(email)s AND EXTRACT(EPOCH FROM (expires - CURRENT_TIMESTAMP)) > 0
                  """, {'email': email})
    return cur.fetchone()

def activate_user(email: str, code: int):
    """ Activate the user
    On success, we remove the line from the activation table because we won't need this info anymore
    """ 
    activation = get_activation(email)
    if not activation:
        raise ExpiredActivationCodeException
    if code != activation['code']:
        raise WrongActivationCodeException
    cur.execute('UPDATE user SET activated = CURRENT_TIMESTAMP WHERE email=%(email)s', {'email': email})
    cur.execute('DELETE FROM activation_codes WHERE user_id=%(id)i', {'id', activation['id']})
    cur.commit()
