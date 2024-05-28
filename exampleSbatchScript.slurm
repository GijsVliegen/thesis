#!/bin/bash -l
#SBATCH --clusters=wice
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=72
#SBATCH --time=3:00:00
#SBATCH --account=lp_dtai1
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=r0810400@kuleuven.be

NrOfVars=${NrOfVars:-5}
Iters=${Iters:-1}
Heuristic=${Heuristic:-"VO"}
Vtree=${Vtree:-"balanced"}
export NrOfVars
export Heuristic
export Vtree

#SBATCH --job-name=sddCompilationTest_${Heuristic}_${Vtree}_${NrOfVars}


#source ~/.bashrc
source activate intelPython

mpirun python3 thesisUbuntu/parallelTimerModule.py $NrOfVars $Iters $Heuristic $Vtree
