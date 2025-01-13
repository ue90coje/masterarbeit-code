#!/bin/bash

#SBATCH --time=40:00:00
#SBATCH --mem=400G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --job-name=generalisierung
#SBATCH --partition=clara

module load JupyterLab/3.1.6-GCCcore-11.2.0
module load dask
module load matplotlib/3.5.2-foss-2021b
jupyter nbconvert --to notebook --execute main.ipynb --output main-output.ipynb
