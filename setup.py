'''
Setup stable.world

'''

from setuptools import find_packages, setup
import versioneer

setup(
    name='stable.world',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Sean Ross-Ross",
    author_email="srossross@gmail.com",
    description="Build reliability tool",
    license="BSD",
    packages=find_packages(),
    install_requires=[
        'click==6.7',
    ],
    entry_points={
        'console_scripts': [
            'stable.world = stable_world.script:main',
        ],
    }
)
