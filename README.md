# Graphs

## Making clean environment.yml file

export only explictly downloaded packages:

`conda env export --from-history --name zerowaste_graphs > environment.yml`

create new from environment.yml file:
`conda env create`

check to see if this works for windows...