#!/bin/bash

# First, create a conda environment.
conda create -n smdm python=3.8 -y

# Now, activate it
conda activate smdm

# Finally, install the dependencies using the script.
conda env update -n smdm -f env.yaml

# Add the new env to ipykernel
python3 -m ipykernel install --user --name smdm --display-name "cis600"
