Stable.World
=============

A Build stability tool

* **Site:** [stable.world](https://stable.world)
* **Build:** [![CircleCI](https://circleci.com/gh/srossross/stable.world/tree/master.svg?style=svg)](https://circleci.com/gh/srossross/stable.world/tree/master)
* **Docs:** [stableworld.readthedocs.io](https://stableworld.readthedocs.io/en/latest/)
* **PyPI:** [![PyPI version](https://badge.fury.io/py/stable.world.svg)](https://badge.fury.io/py/stable.world)

## Installing

### prerequisites
You must have the programs `python` and `pip` installed first. see [installing pip](https://pip.pypa.io/en/stable/installing/)

### Install stable.world command

```
pip install stable.world
```

## Demo


From your machine run the command `stable.world`:

```

$ stable.world

    Welcome to stable.world! (http://stable.world)
    Please login or create an account by entering your email and password:

                          email: test@example.com
                       password: *****

    Logged in as test@example.com


              name your bucket: 'brief-fusarium' ? [Y/n]:

```

## Stabilize your build script

Whether you are using [travis-ci](https://travis-ci.org/), [CircleCI](https://circleci.com/)
or a custom build environment, you can
add the following line to the top of your build script:

```
stable.world use -b <bucket-name> --create-tag <unique-build-number>
```

  * Replace `<bucket-name>` with your bucket name, eg. in the example above
This would be `brief-fusarium`.
  * Replace `<unique-build-number>` with a unique build number of your choice.
    This is going to stave the all of your dependencies you you can easily revert back to
    a successful build. (eg. for travis-ci you may want to write `--create-tag Tavis-Build-${TRAVIS_BUILD_NUMBER}` )

Example:
```
    stable.world use -b brief-fusarium --create-tag "Tavis-Build-${TRAVIS_BUILD_NUMBER}"
```

# When things **wrong** with your build, stable.world is here to help!

Ok now when things hit the fan, we can check what dependencies changed from this
version to the last:

```
stable.world diff -b <bucket-name> -t <from-tag>:<to-tag>
```

* Replace `<bucket-name>` with your bucket name, eg. in the example above
This would be `brief-fusarium`.
* Replace `<from-tag>:<to-tag>` with the tags you want to compare.


In this example, if everything in `Tavis-Build-100` was successful, but there
is an unexplained failure in `Tavis-Build-101` we can see what changed:

```
    stable.world diff -b brief-fusarium -t Tavis-Build-100:Tavis-Build-101
```

Hmm, maybe a new version of package was released and is causing my build to fail...
Lets **pin** the world to the last success and trigger a rebuild.
```
stable.world pin -b <bucket-name> -t <last-success-tag>
```

Example:
```
    stable.world pin -b brief-fusarium -t Tavis-Build-100
```

OK, our devs and testers have pinned the version in the requirements file or fixed the issue
with the new package.

Lets unpin the package

```
stable.world pin -b <bucket-name>
```

Example:
```
    stable.world unpin -b brief-fusarium
```
