#!/bin/bash -l
#SBATCH --clusters=wice
#SBATCH --job-name=sddCompilationTest
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=72
#SBATCH --time=13:00:00
#SBATCH --account=intro_vsc36004
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=r0810400@kuleuven.be

NrOfVars=${NrOfVars:-5}
Iters=${Iters:-1}
Operation=${Operation:0}
Vtree=${Vtree:-"balanced"}
Overhead=${Overhead:-"true"}


#source ~/.bashrc
source activate intelPython

mpirun python3 thesisUbuntu/parallelTimerModule.py $NrOfVars $Iters $Operation $Vtree $Overhead
