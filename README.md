Stable.World
=============

# A Build stability tool


## A New User

will just run
```

$ wrld
>      Enter your email: user@email.com
>   Enter your password:  **** < this will signup or register user
> what languages are you using:
> Your new world name is 'world-name'
> [0] python pip
> [1] node npm


```

## In a build script
```

wrld use world-name --create-tag build001

... build ...

wrld success # you your build number from your CI service. but tags can be anything.
```

## When things go very wrong
Ok now when things hit the fan
```
$wrld diff

> New version of pip package1 was released

```

Hmm a new version of package1 was released and is causing my build to fail...
Lets pin the world to the last success and trigger a rebuild.
```
$wrld pin --last-success
> wrld 'world-name' pinned to tag
```

OK, our devs and testers have pinned the version in the requirements file or fixed the issue
with the new package.

Lets unpin the package

```
$wrld unpin
> wrld 'world-name' unpinned
> Future builds will fetch from upstream!
```
