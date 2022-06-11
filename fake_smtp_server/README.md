# Fake SMTP server

A fake SMTP server that print the content in the console.

## Usage

To run the server using uvicoirn:

```shell
export from_email=noreply@dm-exercise.lan
uvicorn main:app --host 127.0.0.1 --port 8025
```

To listen on all interfaces instead of localhost, use `--host 0.0.0.0`

## API

### /send

| Parameter | Type | Description |
|-----------|:----:|-------------|
| `to` | *string* | Target email |
| `subject` | *string* | Email subject |
| `body` | *string* | Email body |

**Returns**:

* `true` if it is OK

In this exercise, an exception is raised if the email is invalid with the HTTP error code 400.
