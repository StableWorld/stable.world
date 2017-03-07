set -euo pipefail

git clean -xdf dist app
python setup.py sdist
pip install --target app dist/stable.world-*.tar.gz

if [ -z "$(which pyenv)" ]; then
  if [ -z "$(which python2)" ]; then
    echo "WARNING: python2 not installed"
  else
    python2 -m compileall app/
  fi

  if [ -z "$(which python3)" ]; then
    echo "WARNING: python3 not installed"
  else
    python3 -m compileall app/
  fi
else
  pyenv global 2.7.12
  python -m compileall app/
  pyenv global 3.6.0
  python -m compileall app/
fi

python -m zipapp app --python "/usr/bin/env python"  -o ./bin/stable.world
