import os
import psycopg2

conn = psycopg2.connect(host="db", database=os.getenv("POSTGRES_DB"), user="postgres", password=os.getenv("POSTGRES_PASSWORD"))
db = conn.cursor()

class WrongActivationCodeException(Exception):
    """ Raised exception when we try to match a wrong activation code (example: using one from deprecated email) """

class ExpiredActivationCodeException(Exception):
    """ Raised exception when we try to activate an expired code """

def get_user(email: str):
    """ Get user from the email.
    We return the all the user info.
    Password check is not performed with the database because BCrypt is not available
    """
    db.execute('SELECT * FROM users WHERE email=%(email)s', {'email': email})
    return db.fetchone()

def create_user(email: str, hashed_password: str):
    """ Create the user in the database from the email and the hashed password """
    db.execute('INSERT INTO users(email, psw) VALUES(%(email)s)', {'email': email})
    db.commit()

def get_activation(email: str):
    """ Get activation information (email, activation code, expire date UTC, remaining time before expiration) from user's email.
    If user's activation is expired, it returns None
    """
    db.execute("""SELECT email, code, expires, EXTRACT(EPOCH FROM (expires - CURRENT_TIMESTAMP)) remaining_time
                  FROM activation_codes INNER JOIN users ON users.id = user_id
                  WHERE email=%(email)s AND EXTRACT(EPOCH FROM (expires - CURRENT_TIMESTAMP)) > 0
                  """, {'email': email})
    return db.fetchone()

def activate_user(email: str, code: int):
    """ Activate the user
    """ 
    activation = get_activation(email)
    if not activation:
        raise ExpiredActivationCodeException
    if code != activation['code']:
        raise WrongActivationCodeException
    db.execute('UPDATE user SET activated = CURRENT_TIMESTAMP WHERE email=%(email)s', {'email': email})
    # Remove from the activation table because we won't need this info anymore
    db.execute('DELETE FROM activation_codes WHERE user_id=%(id)i', {'id', activation['id']})
    db.commit()
