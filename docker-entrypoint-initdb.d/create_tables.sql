-- Note: https://www.postgresql.org/docs/9.5/datatype-datetime.html
-- For timestamp without time zone, the internally stored value is always in UTC (Universal Coordinated Time, traditionally known as Greenwich Mean Time, GMT). An input value that has an explicit time zone specified is converted to UTC using the appropriate offset for that time zone. If no time zone is stated in the input string, then it is assumed to be in the time zone indicated by the system's TimeZone parameter, and is converted to UTC using the offset for the timezone zone.

SET TIME ZONE 'UTC';

-- DROP TABLE users CASCADE;
-- DROP TABLE activation_codes CASCADE;
-- DROP TABLE auth_tokens CASCADE;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(128) NOT NULL,
    psw VARCHAR(128) NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE('utc')),
    activated TIMESTAMP WITHOUT TIME ZONE,
    UNIQUE(email)
);

CREATE TABLE IF NOT EXISTS activation_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    code SMALLINT NOT NULL CHECK(code BETWEEN 0 and 9999),
    expires TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    CONSTRAINT fk_user_activation_code FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS auth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token VARCHAR(128) NOT NULL,
    expires TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    CONSTRAINT fk_user_auth_token FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
