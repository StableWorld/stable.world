git clean -xdf dist app
python setup.py sdist
pip install --target app dist/stable.world-*.tar.gz

if [ -z "$(which pyenv)" ]; then
  python2 -m compileall app/
  python3 -m compileall app/
else
  pyenv install 2.7.12
  python -m compileall app/
  pyenv install 3.6.0
  python -m compileall app/
fi

python -m zipapp app --python "/usr/bin/env python -SE"  -o stable.world
