import os
import psycopg2

conn = psycopg2.connect(host=os.getenv("POSTGRES_HOST","localhost"), dbname=os.getenv("POSTGRES_DB","postgres"), user=os.getenv("POSTGRES_DB","postgres"), password=os.getenv("POSTGRES_PASSWORD"))
cur = conn.cursor()

class WrongActivationCodeException(Exception):
    """ Raised exception when we try to match a wrong activation code (example: using one from deprecated email) """

class ExpiredActivationCodeException(Exception):
    """ Raised exception when we try to activate an expired code """

class PendingActivationCodeException(Exception):
    """ Raised when an activation code is still active and we want to create a new one """

def get_user(email: str):
    """ Get user from the email.
    We return the all the user info.
    Password check is not performed with the database because BCrypt is not available
    """
    cur.execute('SELECT * FROM users WHERE email=%s', [email])
    return cur.fetchone()

def auth(user_id: int, token: str):
    """ Store the auth token.
    It also clean expired tokens for the user
    """
    cur.execute("DELETE FROM auth_tokens WHERE user_id=%s AND EXTRACT(EPOCH FROM (expires - (NOW() AT TIME ZONE('utc')))) < 0", [user_id])
    cur.execute("""INSERT INTO auth_tokens(user_id, token, expires)
                  VALUES(%(id)s, %(token)s, (NOW() + %(delay)s * interval '1 second') AT TIME ZONE('utc'))
                  RETURNING id
                  """, {'id': user_id, 'token': token, 'delay': os.getenv('TOKEN_DELAY', 600)})
    last_id = cur.fetchone()[0]
    conn.commit()
    
    cur.execute('SELECT id, token, expires FROM auth_tokens WHERE user_id=%(user)s AND id=%(id)s', {'id': last_id, 'user': user_id})
    return cur.fetchone()


def create_user(email: str, hashed_password: str, commit = True):
    """ Create the user in the database from the email and the hashed password """
    cur.execute('INSERT INTO users(email, psw) VALUES(%(email)s, %(psw)s)', {'email': email, 'psw': hashed_password})

def create_activation(email: str, code: str):
    activation = get_activation(email)
    if activation:
        raise PendingActivationCodeException
    print('ca1', activation)
    # clean deprecated if exists
    cur.execute('DELETE FROM activation_codes WHERE user_id=(SELECT id FROM users WHERE email=%s)', [email])
    conn.commit()
    print('ca2', activation)
    user_id=get_user(email)[0]
    cur.execute("""INSERT INTO activation_codes(user_id,code,expires)
                   VALUES(%(u)s, %(code)s, (NOW() + %(delay)s * interval '1 second') AT TIME ZONE('utc'))
                   """, {'u': user_id, 'code': code, 'delay': os.getenv('ACTIVATION_DELAY', 60)})
    conn.commit()


def get_activation(email: str):
    """ Get activation information (email, activation code, expire date UTC, remaining time before expiration) from user's email.
    If user's activation is expired, it returns None
    """
    cur.execute("""SELECT user_id, email, code, expires, EXTRACT(EPOCH FROM (expires - NOW() AT TIME ZONE('utc'))) remaining_time
                  FROM activation_codes INNER JOIN users ON users.id = user_id
                  WHERE email=%s AND EXTRACT(EPOCH FROM (expires - NOW() AT TIME ZONE('utc'))) > 0
                  """, [email])
    return cur.fetchone()

def activate_user(email: str, code: str):
    """ Activate the user
    On success, we remove the line from the activation table because we won't need this info anymore
    """
    activation = get_activation(email)
    if not activation:
        raise ExpiredActivationCodeException
    if code != str(activation[2]):
        raise WrongActivationCodeException
    cur.execute("UPDATE users SET activated = (NOW() AT TIME ZONE('utc')) WHERE email=%s", [email])
    cur.execute('DELETE FROM activation_codes WHERE user_id=%s', [activation[0]])
    conn.commit()
