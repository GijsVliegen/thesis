from mpi4py import MPI
import numpy as np
from heuristicApplier import HeuristicApply, SddVarAppearancesList, SddVtreeCountList
from heuristicApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, EL, VP_EL, ELVAR, VP_ELVAR
from heuristicApplier import AND, OR
from pysdd.sdd import Vtree
import time
import os
import sys
import gc


def doHeuristicTest(heur, heuristicApplier, overheadTime):
    (_, sizeList, varCounts, depthList, timed, noOverheadTimed) = heuristicApplier.doHeuristicApply(heur, overheadTime)
    return timed, noOverheadTimed, sizeList, varCounts, depthList
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
                
def heuristicApply(nrOfVars, iterationsPerNode, operation, heuristic = VO, vtree_type = "balanced", overheadTime = True):

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    overheadTime = True
    # heuristics = [ELVAR, VP_ELVAR, EL, VP_EL]
     #heuristics = [RANDOM, VO, IVO_LR, IVO_RL, VP_KE, VP_EL]
    nrOfSdds = 20
    # iterationsPerNode = 5
    # nrOfVars=20
    # vtree = "balanced"
    

    for i in range(int(nrOfVars/2), int(nrOfVars*5), int(nrOfVars*0.5)):
        randomSeed = i * (rank+1) * 656510
        nrOfClauses = i
        heuristicsTimes = np.zeros((1, iterationsPerNode))
        noOverheadTimes = np.zeros((1, iterationsPerNode))
        heuristicApplier = HeuristicApply(nrOfSdds, nrOfVars, nrOfClauses, operation, randomSeed, vtree_type=vtree_type) 
        allSizeLists = np.zeros((1, iterationsPerNode, nrOfSdds - 1))
        allVarCounts = np.zeros((1, iterationsPerNode, nrOfSdds - 1))
        allDepthLists = np.zeros((1, iterationsPerNode, nrOfSdds - 1))
        for iter in range(iterationsPerNode):
            heuristicApplier.renew()
            if vtree_type == "random":
                vtree_nr = rank * iterationsPerNode * 9 + (int(i / (nrOfVars/2)) -1) * (iterationsPerNode) + iter
                print(f"vtree_nr = {vtree_nr}: iter = {iter}, i = {int(i / (nrOfVars/2))}, rank = {rank}")

                data_directory = os.environ.get("VSC_DATA")
                if data_directory is None:
                    data_directory = ""
                local_file_path = f"randomVtrees/vtree_{vtree_nr}.txt"
                fullPath = os.path.join(data_directory, local_file_path)
                vtree = Vtree.from_file(bytes(fullPath, encoding="utf-8"))
                heuristicApplier.setVtree(vtree)

            heuristicsTimes[:, iter], noOverheadTimes[:, iter], allSizeLists[:, iter], allVarCounts[:, iter], allDepthLists[:, iter]\
                    = doHeuristicTest(heuristic, heuristicApplier, overheadTime)
        del heuristicApplier
        gc.collect()

        averageSizeList = np.array(allSizeLists).mean(axis = 1)

        # print(averageSizeList)

        averageVarCounts = np.array(allVarCounts).mean(axis = 1)
        averageDepthLists = np.array(allDepthLists).mean(axis = 1)
        if rank == 0:
            heuristicTimesMatrices = np.empty((size, 1, iterationsPerNode))
            noOverheadTimesMatrices = np.empty((size, 1, iterationsPerNode))
            heuristicSizesMatrices = np.empty((size, 1, nrOfSdds-1))
            heuristicVarCountMatrices = np.empty((size, 1, nrOfSdds-1))
            heuristicDepthMatrices = np.empty((size, 1, nrOfSdds-1))
        else:
            heuristicTimesMatrices = None
            noOverheadTimesMatrices = None
            heuristicSizesMatrices = None
            heuristicVarCountMatrices = None
            heuristicDepthMatrices = None
        comm.Gather(heuristicsTimes, heuristicTimesMatrices , root=0)
        comm.Gather(noOverheadTimes, noOverheadTimesMatrices, root=0)
        comm.Gather(averageSizeList, heuristicSizesMatrices , root=0)
        comm.Gather(averageVarCounts, heuristicVarCountMatrices , root=0)
        comm.Gather(averageDepthLists, heuristicDepthMatrices , root=0)
        if rank == 0:
            allHeuristicTimes = np.concatenate(heuristicTimesMatrices, axis=1)
            allNoOverheadTimes = np.concatenate(noOverheadTimesMatrices, axis=1)
            averageSizeList = np.array(heuristicSizesMatrices).mean(axis = 0)
            averageVarCounts = np.array(heuristicVarCountMatrices).mean(axis = 0)
            averageDepthLists = np.array(heuristicDepthMatrices).mean(axis = 0)
            testName = "test" if overheadTime else "noOverhead"
            operationStr = "OR" if operation == OR else "AND"
            data_directory = os.environ.get("VSC_DATA")
            if data_directory is None:
                data_directory = ""
            results = [allHeuristicTimes, averageSizeList, averageVarCounts, averageDepthLists]#, averageMemLists]
            for metric, res in zip(["heuristic", "sizes", "varCounts", "depth"], results):#, "memUsage"], results):
                local_file_path = f"output/{metric}/{testName}_{nrOfSdds}_{nrOfVars}_{operationStr}_{vtree_type}_{[heuristic]}_{nrOfClauses}.txt"
                fullPath = os.path.join(data_directory, local_file_path)
                os.makedirs(os.path.dirname(fullPath), exist_ok=True)
                with open(fullPath, 'w') as file:
                    file.write(f"{res[0].tolist()}\n") 
            local_file_path = f"output/heuristic/noOverhead_{nrOfSdds}_{nrOfVars}_{operationStr}_{vtree_type}_{[heuristic]}_{nrOfClauses}.txt"
            fullPath = os.path.join(data_directory, local_file_path)
            with open(fullPath, 'w') as file:
                file.write(f"{allNoOverheadTimes.tolist()}\n") 
        gc.collect()

def randomRatiosApplyExperiment(nrOfVars, iterationsPerNode, operation, heuristic = VO, vtree_type = "balanced"):
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    overheadTime = True
    # heuristics = [ELVAR, VP_ELVAR, EL, VP_EL]
     #heuristics = [RANDOM, VO, IVO_LR, IVO_RL, VP_KE, VP_EL]
    nrOfSdds = 20
    # iterationsPerNode = 5
    # nrOfVars=20
    # vtree = "balanced"
    
    randomSeed = (rank+1) * 656510
    heuristicsTimes = np.zeros((1, iterationsPerNode))
    noOverheadTimes = np.zeros((1, iterationsPerNode))
    heuristicApplier = HeuristicApply(nrOfSdds, nrOfVars, 1, operation, randomSeed, vtree_type=vtree_type) 
    allSizeLists = np.zeros((1, iterationsPerNode, nrOfSdds - 1))
    allVarCounts = np.zeros((1, iterationsPerNode, nrOfSdds - 1))
    allDepthLists = np.zeros((1, iterationsPerNode, nrOfSdds - 1))
    for iter in range(iterationsPerNode):
        heuristicApplier.renew()
        if vtree_type == "random": #moet nog getest worden
            # vtree_nr = rank * iterationsPerNode + iter
            # print(f"vtree_nr = {vtree_nr}: iter = {iter}, rank = {rank}")

            # data_directory = os.environ.get("VSC_DATA")
            # if data_directory is None:
            #     data_directory = ""
            # local_file_path = f"randomVtrees/vtree_{vtree_nr}.txt"
            # fullPath = os.path.join(data_directory, local_file_path)
            # vtree = Vtree.from_file(bytes(fullPath, encoding="utf-8"))
            # heuristicApplier.setVtree(vtree)
            pass
        #(finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime)
        _, allSizeLists[:, iter], allVarCounts[:, iter], allDepthLists[:, iter], heuristicsTimes[:, iter], noOverheadTimes[:, iter]\
                = heuristicApplier.randomRatiosApply(heuristic)
    del heuristicApplier
    gc.collect()

    averageSizeList = np.array(allSizeLists).mean(axis = 1)

    # print(averageSizeList)

    averageVarCounts = np.array(allVarCounts).mean(axis = 1)
    averageDepthLists = np.array(allDepthLists).mean(axis = 1)
    if rank == 0:
        heuristicTimesMatrices = np.empty((size, 1, iterationsPerNode))
        noOverheadTimesMatrices = np.empty((size, 1, iterationsPerNode))
        heuristicSizesMatrices = np.empty((size, 1, nrOfSdds-1))
        heuristicVarCountMatrices = np.empty((size, 1, nrOfSdds-1))
        heuristicDepthMatrices = np.empty((size, 1, nrOfSdds-1))
    else:
        heuristicTimesMatrices = None
        noOverheadTimesMatrices = None
        heuristicSizesMatrices = None
        heuristicVarCountMatrices = None
        heuristicDepthMatrices = None
    comm.Gather(heuristicsTimes, heuristicTimesMatrices , root=0)
    comm.Gather(noOverheadTimes, noOverheadTimesMatrices, root=0)
    comm.Gather(averageSizeList, heuristicSizesMatrices , root=0)
    comm.Gather(averageVarCounts, heuristicVarCountMatrices , root=0)
    comm.Gather(averageDepthLists, heuristicDepthMatrices , root=0)
    if rank == 0:
        allHeuristicTimes = np.concatenate(heuristicTimesMatrices, axis=1)
        allNoOverheadTimes = np.concatenate(noOverheadTimesMatrices, axis=1)
        averageSizeList = np.array(heuristicSizesMatrices).mean(axis = 0)
        averageVarCounts = np.array(heuristicVarCountMatrices).mean(axis = 0)
        averageDepthLists = np.array(heuristicDepthMatrices).mean(axis = 0)
        testName = "test" if overheadTime else "noOverhead"
        operationStr = "OR" if operation == OR else "AND"
        data_directory = os.environ.get("VSC_DATA")
        if data_directory is None:
            data_directory = ""
        results = [allHeuristicTimes, averageSizeList, averageVarCounts, averageDepthLists]#, averageMemLists]
        for metric, res in zip(["heuristic", "sizes", "varCounts", "depth"], results):#, "memUsage"], results):
            local_file_path = f"output/randomRatios/{metric}/{testName}_{nrOfSdds}_{nrOfVars}_{operationStr}_{vtree_type}_{[heuristic]}.txt"
            fullPath = os.path.join(data_directory, local_file_path)
            os.makedirs(os.path.dirname(fullPath), exist_ok=True)
            with open(fullPath, 'w') as file:
                file.write(f"{res[0].tolist()}\n") 
        local_file_path = f"output/randomRatios/heuristic/noOverhead_{nrOfSdds}_{nrOfVars}_{operationStr}_{vtree_type}_{[heuristic]}.txt"
        fullPath = os.path.join(data_directory, local_file_path)
        with open(fullPath, 'w') as file:
            file.write(f"{allNoOverheadTimes.tolist()}\n") 
    gc.collect()

def main():
    args = sys.argv[1:]
    baseArgs = [16, 1, VO, "balanced"]
    heuristicConvertDict = {"RANDOM":RANDOM, "VO":VO, "IVO_LR":IVO_LR, "IVO_RL":IVO_RL, "VP_EL": VP_EL, "VP_KE": VP_KE, "VP_ELVAR": VP_ELVAR}
    modifier = [lambda x: int(x), lambda x: int(x), lambda x: heuristicConvertDict[x], lambda x: x]
    try:
        for i in range(len(args)):
            baseArgs[i] = modifier[i](args[i])
    except ValueError:
        print("Error: Please provide 4 valid arguments.")
        return
    # print(baseArgs)
    # heuristicApply(baseArgs[0], baseArgs[1], OR, baseArgs[2], baseArgs[3])
    # heuristicApply(baseArgs[0], baseArgs[1], AND, baseArgs[2], baseArgs[3])
    randomRatiosApplyExperiment(baseArgs[0], baseArgs[1], OR, baseArgs[2], baseArgs[3])
    randomRatiosApplyExperiment(baseArgs[0], baseArgs[1], AND, baseArgs[2], baseArgs[3])

if __name__ == "__main__":
    # Call main function with command line arguments excluding script name
    main()
