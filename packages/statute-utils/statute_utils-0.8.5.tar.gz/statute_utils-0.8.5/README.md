# statute-utils

![Github CI](https://github.com/justmars/statute-utils/actions/workflows/ci.yml/badge.svg)

Philippine statutory law:

1. pattern matching
2. unit retrieval
3. database creation
4. template creation

> [!IMPORTANT]
> When modifying a database structure, consider four inter-related parts:
>
> 1. The pythonic object, e.g. `NamedTuple`
> 2. The representation of such in the prospective database
> 3. The documentation of the pythonic object found in `/docs`
> 4. The use of all of the above in downstream [decision-utils](https://github.com/justmars/decision-utils).

## Run

```sh
just --list # see recipes
just start # install
just dumpenv # configure .env

builder # list command line recipes from pyproject.toml script
builder interim-db # show statute files in /data

just build-trees # creates base on .env-based DB_FILE
```

## Docs

```sh
mkdocs serve
```
