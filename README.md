# Graphs

doesn't export pip packages, but cleaner env file

this has no version number:

`conda env export --from-history --name graph_network > environment.yml`

this has no build number:

`conda env export --no-builds --name graph_network > environment.yml`

create new:

`conda env create`