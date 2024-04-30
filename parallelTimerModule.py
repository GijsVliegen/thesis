from mpi4py import MPI
import numpy as np
from heuristicApplier import HeuristicApply, SddVarAppearancesList, SddVtreeCountList
from heuristicApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, \
    EL
from heuristicApplier import AND, OR
import timeit

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

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
                
def heuristicApply(heuristics, operation, overheadTime):
    nrOfSdds=20
    iterationsPerNode = 5
    nrOfVars=20
    vtree = "balanced"
    
    if rank == 0:
        data = [(i, i + iterationsPerNode) for i in range(1, iterationsPerNode*size, iterationsPerNode)]
    else:
        data = None
    data = comm.scatter(data, root=0)

    for i in range(int(nrOfVars/2), int(nrOfVars), int(nrOfVars*0.5)):
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
            with open(f"output/heuristic/{name}_{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt", 'w') as file:
                file.write(f"experiment: sdds: {nrOfSdds}, vars: {nrOfVars}, operation = {operationStr}, vtree = {vtree}, heuristiek = {heuristics}" + '\n')
                for i in range(len(heuristics)):
                    file.write(f"heuristiek {heuristics[i]} times: {allHeuristicTimes[i]}\n")

heuristicApply([8, 7], OR, True)