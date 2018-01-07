set +xe
curl -o docker.tgz https://download.docker.com/linux/static/stable/x86_64/docker-17.06.2-ce.tgz
tar --extract \
  --file docker.tgz \
  --strip-components 1 \
  --directory /usr/local/bin/
apt-get install -y make
