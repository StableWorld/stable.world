set +xe
apk add --no-cache \
  openssl \
  make \
  curl curl-dev \
  py-pip \
  sudo \
  bash

pip install -q docker-compose==1.16.1
