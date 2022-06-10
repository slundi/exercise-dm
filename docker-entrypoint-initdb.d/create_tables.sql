-- Note: https://www.postgresql.org/docs/9.5/datatype-datetime.html
-- For timestamp with time zone, the internally stored value is always in UTC (Universal Coordinated Time, traditionally known as Greenwich Mean Time, GMT). An input value that has an explicit time zone specified is converted to UTC using the appropriate offset for that time zone. If no time zone is stated in the input string, then it is assumed to be in the time zone indicated by the system's TimeZone parameter, and is converted to UTC using the offset for the timezone zone.

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(128) NOT NULL,
    psw BYTEA(24) NOT NULL,
    created TIMESTAMP WITH TIME ZONE NOT NULL,
    activated TIMESTAMP WITH TIME ZONE,
    UNIQUE(email)
);

CREATE TABLE IF NOT EXISTS activation_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    code SMALLINT NOT NULL CHECK(code BETWEEN 0 and 9999),
    expires TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id)
);
