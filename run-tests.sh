#!/bin/bash

docker-compose -f docker-compose-tests.yml down --remove-orphans
docker-compose -f docker-compose-tests.yml build --force-rm --pull
docker-compose -f docker-compose-tests.yml up --exit-code-from test_apis
