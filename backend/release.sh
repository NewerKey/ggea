#!/bin/sh

set -e

IMAGE_ID=$(docker inspect ${GCP_REGISTRY_IMAGE} --format={{.Id}})
PAYLOAD='{"updates": [{"type": "web", "docker_image": "'"$IMAGE_ID"'"}]}'

curl -n -X PATCH https://api.google.com/apps/$GCP_SERVICE_NAME/formation \
  -d "${PAYLOAD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.googlecloud+json; version=3.docker-releases" \
  -H "Authorization: Bearer ${GCP_SA_KEY}"