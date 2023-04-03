## Requirements
- pyenv
- pypoetry

## Installation
```shell
pyenv init
pyenv install 3.11
pyenv local 3.11
poetry config virtualenvs.in-project true
poetry env use 3.11
poetry install && poetry run pre-commit install
```

## Execution
```shell
npx -y nodemon main.py --print-test-tree

# or

pnpm dlx nodemon main.py --print-test-tree
```

## Branch naming
Branch names should follow this spec:
```
feat/my-branch-name
^   ^ ^______________ letters, numbers or hyphen (-)
 \   \_______________ slash (/) is required!
  \__________________ one of: fix, feat, docs, refactor or test
```
