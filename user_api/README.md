# User API

User API server

## Usage

To run the server using uvicorn:

```shell
export POSTGRES_HOST=localhost
export POSTGRES_DB=dm
export POSTGRES_USER=dm
export POSTGRES_PASSWORD=top-secret
uvicorn main:app --host 127.0.0.1 --port 8080
```

To listen on all interfaces instead of localhost, use `--host 0.0.0.0`

**YOU NEED A POSTGRES SERVER RUNNING WITH THE ABOVE CONFIGURED ENV VARIABLES**

## API

All data are sent using the POST method

### /register

| Parameter | Type | Description |
|-----------|:----:|-------------|
| `email` | *string* | User's email |
| `password` | *string* | User's password |

**Returns**:

JSON:

* `ok`: a boolean that says if it is OK
* `reason`: OPTIONAL field that is set when ok is `false` to tell you the problem

### /login

| Parameter | Type | Description |
|-----------|:----:|-------------|
| `email` | *string* | User's email |
| `password` | *string* | User's password |

**Returns**:

A 401 error if the email and/or the password is wrong. Otherwise it is a JSON dictionnary:

* `token`: generated token for the connexion
* `expires`: when the token should expires in date time UTC

### /validate

Validate an activation code

| Parameter | Type | Description |
|-----------|:----:|-------------|
| `email` | *string* | User's email |
| `code` | *string* | The code that was sent by mail |

**Returns**:

JSON:

* `ok`: a boolean that says if it is OK
* `reason`: OPTIONAL field that is set when ok is `false` to tell you the problem
