#!/bin/sh

set -e -x

LOCATION=europe-west6-docker.pkg.dev
PROJECT=distalog
REPOSITORY=temp-api


IMAGE=$(docker build -q .)
docker tag ${IMAGE} ${LOCATION}/${PROJECT}/${REPOSITORY}/api
docker push ${LOCATION}/${PROJECT}/${REPOSITORY}/api