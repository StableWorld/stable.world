git clean -xdf dist app
python setup.py sdist
pip install --target app dist/stable.world-*.tar.gz
python2 -m compileall app/
python3 -m compileall app/

python -m zipapp app --python "/usr/bin/env python -SE"  -o stable.world
