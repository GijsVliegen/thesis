#!/bin/bash -l
#SBATCH --clusters=wice
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=30:00
#SBATCH --account=intro_vsc36004
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=r0810400@kuleuven.be

Heuristic=${Heuristic:-8}
export Heuristic

#SBATCH --job-name=sddCompilationTest_${Heuristic}_${Vtree}_${NrOfVars}


#source ~/.bashrc
source activate intelPython

python3 thesisUbuntu/BCFormulaParser.py $Heuristic ${SLURM_ARRAY_TASK_ID}