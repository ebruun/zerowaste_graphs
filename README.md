# Graphs

doesn't export pip packages, but cleaner env file

this has no version number:

`conda env export --from-history --name zerowaste_graph > environment.yml`

this has no build number:

`conda env export --no-builds --name zerowaste_graph > environment.yml`

create new:

`conda env create`