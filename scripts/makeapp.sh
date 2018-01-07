set -eux

git clean -xdf dist app
docker build -f scripts/Dockerfile -t makeapp:build .
docker create --name extract makeapp:build
docker cp extract:/project/bin/stable.world ./bin/stable.world
ls -la bin/stable.world
echo "OK!"
