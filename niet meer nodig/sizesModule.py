from heuristicApplier import HeuristicApply
from heuristicApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, \
    EL, VP_EL, heuristicDict
from heuristicApplier import OR, AND
import matplotlib.pyplot as plt

import timeit
import numpy as np
def getHeuristicName(heuristicInt):
    return heuristicDict[heuristicInt]

def doRandomOrderTest(randomApplier, operation):
    (_, sizeList, _) = randomApplier.doHeuristicApply(RANDOM, operation)
    return max(sizeList)

def randomOrderMaxSizeVariation():
    nrOfSdds=20
    nrOfVars=16
    operation = OR 
    iterations = 1000
    vtree = "balanced"
    operationStr = "OR" if operation == OR else "AND"
    for nrOfClauses in range(int(nrOfVars*0.2), nrOfVars*5, int(nrOfVars*0.2)):
        randomApplier = HeuristicApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type=vtree)
        maxSizeList = []
        for i in range(iterations):
            maxSizeList.append(doRandomOrderTest(randomApplier, operation))
        counts, bins, _ = plt.hist(maxSizeList, bins=30, edgecolor='black', alpha=0)  # Using alpha=0 makes bars invisible
        plt.plot(bins[:-1], counts, linestyle='-', marker='o') #lijn tussen de toppen van de histogram
        plt.xlabel('Aantal compilaties')
        plt.ylabel('Maximum grootte')
        plt.title("Maximum grootte voor willekeurige compilatiesequenties")
        plt.xscale('log')
        plt.savefig(f"figs/sizes/randomVariation/20_{nrOfVars}_{nrOfClauses}_{vtree}_{operationStr}.png") #savefig moet blijkbaar voor show() komen
        plt.clf()

def doHeuristicTest(heuristics, randomApplier, operation):
    sizeListsHeuristics = []
    varCountsHeuristics = []
    depthListHeuristics = []
    for heur in heuristics:
        (_, sizeList, varCounts, depthList, _) = randomApplier.doHeuristicApply(heur, operation)
        sizeListsHeuristics.append(sizeList)
        varCountsHeuristics.append(varCounts)
        depthListHeuristics.append(depthList)
    return sizeListsHeuristics, varCountsHeuristics, depthListHeuristics


def heuristicsApply(heuristics, nrOfVars, vtree):
    nrOfSdds=20
    operation = OR 
    iterations = 100
    operationStr = "OR" if operation == OR else "AND"
    for nrOfClauses in range(int(nrOfVars*0.25), nrOfVars*5, int(nrOfVars*0.25)):
        print(f"nr of clauses = {nrOfClauses}")
        heuristicApplier = HeuristicApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type=vtree)
        allSizeLists = []
        allVarCounts = []
        allDepthLists = []
        for iter in range(iterations):
            heuristicApplier.renew()
            sizeListsHeuristics, varCountsHeuristics, depthListHeuristics = doHeuristicTest(heuristics, heuristicApplier, operation)
            allSizeLists.append(sizeListsHeuristics)
            allVarCounts.append(varCountsHeuristics)
            allDepthLists.append(depthListHeuristics)
        averageSizeList = np.array(allSizeLists).mean(axis = 0).tolist()
        averageVarCounts = np.array(allVarCounts).mean(axis = 0).tolist()
        averageDepthLists = np.array(allDepthLists).mean(axis = 0).tolist()
        with open(f"output/sizes/{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt", 'w') as file:
            for i in range(len(averageSizeList)):
                file.write(f"{averageSizeList[i]}\n")
        with open(f"output/varCounts/{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt", 'w') as file:
            for i in range(len(averageVarCounts)):
                file.write(f"{averageVarCounts[i]}\n")
        with open(f"output/depth/{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt", 'w') as file:
            for i in range(len(averageDepthLists)):
                file.write(f"{averageDepthLists[i]}\n")


def __main__():
    # heuristieken: VP_EL, VO, VP_KE, IVO_LR, IVO_RL, RANDOM
    heuristics = [9, 10, 5, 8]
    # heuristics = [RANDOM, VP_KE, VP_EL, IVO_LR, VO, IVO_RL]
    # heuristicsApply(heuristics, 16, "balanced")
    # 
    #randomOrderMaxSizeVariation()
        
__main__()