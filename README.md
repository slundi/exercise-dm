# exercise-dm

Job interview exercise: Building a user registration API

## Subject

### Context

Our client handles user registrations. To do so, user creates an account and we send a code by email to verify the account.

As a core API developer, you are responsible for building this feature and expose it through API.

### Specifications

You have to manage a user registration and his activation.

The API must support the following use cases:

* Create a user with an email and a password.
* Send an email to the user with a 4 digits code.
* Activate this account with the 4 digits code received. For this step, we consider a `BASIC AUTH` is enough to check if he is the right user.
* The user has only one minute to use this code. After that, an error should be raised.

Design and build this API. You are completely free to propose the architecture you want.

### What do we expect

* Your application should be in Python.
* We expect to have a level of code quality which could go to production.
* Using frameworks is allowed only for routing, dependency injection, event dispatcher, db connection. Don't use magic (ORM for example)! We want to see **your** implementation.
* Use the DBMS you want (except SQLite).
* Consider the SMTP server as a third party service offering an HTTP API. You can mock the call, use a local SMTP server running in a container, or simply print the 4 digits in console. But do not forget in your implementation that **it is a third party service**.
* Your code should be tested.
* Your application has to run within a docker containers.
* You should provide us the source code (or a link to GitHub)
* You should provide us the instructions to run your code and your tests. We should not install anything except docker/docker-compose to run you project.
* You should provide us an architecture schema.

## Solution

TODO: diagram

### Running tests

TODO: how to run them

### Installation

TODO

### Security

Password hashes are stored in the database using Bcrypt: the hash is slow so it is good against brute forece cracking and there is salt so you can't compare hashes.

To improve security we can set password rules (min/max length, digit required, upper and lower case characters required and at least one special characters) but this is not implemented in this exercise.

User account activation send the 4 digits code once. If the user loses his code, a new one is generated with a new valid period. Only one registration code can be active.

Traffic is running through HTTP so traffic is not encrypted. You'll need to install a web server with HTTPS support in front of the Docker stack.

Only the web server port is exposed in the Docker stack. It does not protect from any attack. To protect it, you can use **fail2ban** with **nginx** server in front of the auth service as followed:

**/etc/fail2ban/filter.d/wrongauth.conf**:

```text
[Definition]
failregex = ^<HOST> -.* 401
ignoreregex =
```

In **/etc/fail2ban/jail.con**:

```text
[wrongauth]
enabled = true
filter = wrongauth
action = shorewall 
    %(mta)s-whois-lines[name=%(__name__)s, dest="%(destemail)s", logpath=%(logpath)s, chain="%(chain)s", sendername="%(sendername)s"]
logpath = /var/log/nginx*/*access*.log
banTime = 600 # 10 minutes
findTime = 60
maxretry = 10 #
```

You can also detect bad requests (HTTP error 400) in order to ban clients that are trying to find exploits (replace 401 with 400 in the previous code snippet).

There is also [Crowdsec](https://crowdsec.net/) that can replace fail2ban and it have a community detection system.
