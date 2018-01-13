from python:3.6
# set -eux
COPY . /project
WORKDIR /project
# git clean -xdf dist app

RUN python setup.py sdist --quiet
RUN pip install --quiet --target app dist/stable.world-*.tar.gz
RUN python -m compileall app/
RUN python -m zipapp app -o ./bin/stable.world.pyz

RUN cat ./app/header.sh ./bin/stable.world.pyz > ./bin/stable.world
# TODO: windows deploy
# cat ./app/header.bat ./bin/stable.world.pyz > ./bin/stable.world.bat
RUN chmod +x ./bin/stable.world
