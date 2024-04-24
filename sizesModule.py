from randomOrderApplier import RandomOrderApply
from randomOrderApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, \
    EL, VP_EL, heuristicDict
from randomOrderApplier import OR, AND
import matplotlib.pyplot as plt

import timeit
import numpy
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
        randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type=vtree)
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
    for heur in heuristics:
        (_, sizeList, _) = randomApplier.doHeuristicApply(heur, operation)
        sizeListsHeuristics.append(sizeList)
    return sizeListsHeuristics


def heuristicsApply(heuristics, nrOfVars, vtree):
    nrOfSdds=20
    operation = OR 
    iterations = 1
    operationStr = "OR" if operation == OR else "AND"
    for nrOfClauses in range(int(nrOfVars*0.25), nrOfVars*5, int(nrOfVars*0.25)):
        print(f"nr of clauses = {nrOfClauses}")
        randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type=vtree)
        for i in range(iterations):
            randomApplier.renew()
            sizeListsHeuristics = doHeuristicTest(heuristics, randomApplier, operation)
            for (heur, sizeList) in zip(heuristics, sizeListsHeuristics):
                plt.plot(range(nrOfSdds-1), sizeList, marker='o', \
                            linestyle='-', label=getHeuristicName(heur))
            plt.xlabel('Index tussenresultaat')
            plt.ylabel('Grootte van tussenresultaat')
            plt.title(f"Groottes tijdens compilatiesequentie voor ratio {nrOfClauses/nrOfVars}")
            plt.legend()
            plt.yscale('log')
            plt.savefig(f"figs/sizes/{vtree}/20_{nrOfVars}_{nrOfClauses}_{heuristics}_{operationStr}.png") #savefig moet blijkbaar voor show() komen
            plt.clf()


def __main__():
    #heuristieken: VP_EL, VO, VP_KE, IVO_LR, IVO_RL, RANDOM
    heuristics = [RANDOM, VP_EL, VO, VP_KE, IVO_LR, IVO_RL]
    heuristicsApply(heuristics, 24, "balanced")
    heuristicsApply(heuristics, 24, "right")
    #randomOrderMaxSizeVariation()
        
__main__()