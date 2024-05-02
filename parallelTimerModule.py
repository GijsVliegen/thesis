from mpi4py import MPI
import numpy as np
from heuristicApplier import HeuristicApply, SddVarAppearancesList, SddVtreeCountList
from heuristicApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, EL, VP_EL
from heuristicApplier import AND, OR
import timeit
import os
import sys


def doHeuristicTest(heuristics, heuristicApplier, operation, overheadTime):
    timeHeuristics = []
    for heur in heuristics:
        if (overheadTime):
            timeHeuristics.append(timeit.timeit(lambda: heuristicApplier.doHeuristicApply(heur, operation), number = 1))
        else:
            (_, _, time) = heuristicApplier.doHeuristicApply(heur, operation, overheadTime)
            timeHeuristics.append(time)
    return timeHeuristics

# def heuristicsApply(heuristics, operation, overheadTime):
#     nrOfSdds=20
#     iterations = 2000
#     nrOfVars=20
#     for i in range(int(nrOfVars/2), int(nrOfVars*5), int(nrOfVars*0.5)):
#         print(f"nr of clauses = {i}")
#         nrOfClauses = i
#         vtree = "balanced"
#         name = "test" if overheadTime else "noOverhead"
#         operationStr = "OR" if operation == OR else "AND"
#         heuristicsTimes = []
#         randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type=vtree)
#         for i in heuristics:
#             heuristicsTimes.append([])
#         for _ in range(iterations):
#             randomApplier.renew()
#             timeHeuristics = doHeuristicTest(heuristics, randomApplier, operation, overheadTime)
#             for i in range(len(timeHeuristics)):
#                 heuristicsTimes[i].append(timeHeuristics[i])
#         with open(f"output/heuristic/{name}_{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt", 'w') as file:
#             file.write(f"experiment: sdds: {nrOfSdds}, vars: {nrOfVars}, operation = {operationStr}, vtree = {vtree}, heuristiek = {heuristics}" + '\n')
#             for i in range(len(heuristics)):
#                 file.write(f"heuristiek {heuristics[i]} times: {heuristicsTimes[i]}\n")
                
def heuristicApply(nrOfVars, iterationsPerNode, vtree, overheadTime):

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    heuristics = [RANDOM, VO, IVO_LR, IVO_RL, VP_KE, VP_EL]
    operation = OR
    nrOfSdds = 20
    # iterationsPerNode = 5
    # nrOfVars=20
    # vtree = "balanced"
    

    for i in range(int(nrOfVars/2), int(nrOfVars*5), int(nrOfVars*0.5)):
        nrOfClauses = i
        heuristicsTimes = np.zeros((len(heuristics), iterationsPerNode))
        heuristicApplier = HeuristicApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type=vtree)
        for iter in range(iterationsPerNode):
            heuristicApplier.renew()
            heuristicsTimes[:, iter] = doHeuristicTest(heuristics, heuristicApplier, operation, overheadTime)
        if rank == 0:
            heuristicTimesMatrices = np.empty((size, len(heuristics), iterationsPerNode))
        else:
            heuristicTimesMatrices = None
        comm.Gather(heuristicsTimes, heuristicTimesMatrices , root=0)
        if rank == 0:
            allHeuristicTimes = np.concatenate(heuristicTimesMatrices, axis=1)
            name = "test" if overheadTime else "noOverhead"
            operationStr = "OR" if operation == OR else "AND"
            data_directory = os.environ.get("VSC_DATA")
            if data_directory is None:
                data_directory = ""
            local_file_path = f"output/heuristic/{name}_{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt"
            fullPath = os.path.join(data_directory, local_file_path)
            os.makedirs(os.path.dirname(fullPath), exist_ok=True)
            with open(fullPath, 'w') as file:
                file.write(f"experiment: sdds: {nrOfSdds}, vars: {nrOfVars}, operation = {operationStr}, vtree = {vtree}, heuristiek = {heuristics}" + '\n')
                for i in range(len(heuristics)):
                    file.write(f"heuristiek {heuristics[i]} times: {allHeuristicTimes[i]}\n")

def main():
    args = sys.argv[1:]
    baseArgs = [10, 20, "balanced", True]
    modifier = [lambda x: int(x), lambda x: int(x), lambda x: x, lambda x: x.lower() in ('true', '1', 't', 'y', 'yes')]
    try:
        for i in range(len(args)):
            baseArgs[i] = modifier[i](args[i])
    except ValueError:
        print("Error: Please provide 4 valid arguments.")
        return
    # print(baseArgs)
    heuristicApply(baseArgs[0], baseArgs[1], baseArgs[2], baseArgs[3])

if __name__ == "__main__":
    # Call main function with command line arguments excluding script name
    main()