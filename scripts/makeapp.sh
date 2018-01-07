set -eux

git clean -xdf dist app

docker run -v $(pwd):/sw -w /sw circleci/python:3.6 \
  python setup.py sdist

docker run -v $(pwd):/sw -w /sw circleci/python:3.6 \
  pip install --target app dist/stable.world-*.tar.gz

docker run -v $(pwd):/sw -w /sw circleci/python:2.7 \
  python -m compileall app/

docker run -v $(pwd):/sw -w /sw circleci/python:3.6 \
  python -m compileall app/

docker run  -v $(pwd):/sw -w /sw circleci/python:3.6 \
  python -m zipapp app -o ./bin/stable.world.pyz

cat ./app/header.sh ./bin/stable.world.pyz > ./bin/stable.world
# TODO: windows deploy
# cat ./app/header.bat ./bin/stable.world.pyz > ./bin/stable.world.bat
chmod +x ./bin/stable.world
