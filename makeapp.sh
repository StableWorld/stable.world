set -euo pipefail

git clean -xdf dist app
python3 setup.py sdist
pip install --target app dist/stable.world-*.tar.gz

python2 -m compileall app/
python3 -m compileall app/

python3 -m zipapp app --python "/usr/bin/env python"  -o ./bin/stable.world
chmod +x ./bin/stable.world
