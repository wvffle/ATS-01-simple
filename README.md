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
Branch names should follow this spec:
```
feat/my-branch-name
^   ^ ^______________ letters, numbers or hyphen (-)
 \   \_______________ slash (/) is required!
  \__________________ one of: fix, feat, docs, refactor or test
```
