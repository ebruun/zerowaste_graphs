# Graphs

## Making clean environment.yml file

export only explictly downloaded packages:

`conda env export --from-history --name zerowaste_graphs > environment.yml`

create new from environment.yml file:
`conda env create`

check to see if this works for windows...

## Linting and Pre-commit

make sure .pre-commit-config.yaml file is up to date

language_version: python (use system version of python)

run this: `pre-commit install`

in .vscode/settings.json make sure formatonsave = TRUE