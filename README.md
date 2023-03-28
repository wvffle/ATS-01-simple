## Requirements
- pyenv
- pypoetry

## Installation
```shell
pyenv init
pyenv install 3.11
pyenv local 3.11
poetry env use 3.11
poetry install && poetry run pre-commit install
```

## Execution
```shell
npx -y nodemon ats-project-simple/main.py

# or

pnpm dlx nodemon ats-project-simple/main.py
```

## Branch naming
```
start branch name with one of fix|feat|docs|refactor|test
```
