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
    for heur in heuristics:
        (_, sizeList, varCounts, _) = randomApplier.doHeuristicApply(heur, operation)
        sizeListsHeuristics.append(sizeList)
        varCountsHeuristics.append(varCounts)
    return sizeListsHeuristics, varCountsHeuristics


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
        for iter in range(iterations):
            heuristicApplier.renew()
            sizeListsHeuristics, varCountsHeuristics = doHeuristicTest(heuristics, heuristicApplier, operation)
            allSizeLists.append(sizeListsHeuristics)
            allVarCounts.append(varCountsHeuristics)
        averageSizeList = np.array(allSizeLists).mean(axis = 0).tolist()
        averageVarCounts = np.array(allVarCounts).mean(axis = 0).tolist()
        with open(f"output/sizes/{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt", 'w') as file:
            for i in range(len(averageSizeList)):
                file.write(f"{averageSizeList[i]}\n")
        with open(f"output/varCounts/{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt", 'w') as file:
            for i in range(len(averageVarCounts)):
                file.write(f"{averageVarCounts[i]}\n")

def graphHeuristicApply(heuristics, nrOfVars, vtree):
    nrOfSdds=20
    operation = OR 
    operationStr = "OR" if operation == OR else "AND"
    colors = ['red', 'blue', "green", "orange", "purple", "brown", "yellow", "pink"]
    #sizes
    for nrOfClauses in range(int(nrOfVars*0.25), nrOfVars*5, int(nrOfVars*0.25)):
        filename = f"output/sizes/{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt"
        with open(filename, 'r') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]
        for (index, line) in enumerate(lines):
            try:
                current_list = eval(line)
            except SyntaxError:
                print(f"Invalid list format in line: {line}")
            plt.plot(range(1, nrOfSdds), current_list, marker='o', \
                        linestyle='-', color = colors[index], label=getHeuristicName(heuristics[index]))
        plt.xlabel('Index tussenresultaat')
        plt.ylabel('Grootte van tussenresultaat')
        plt.title(f"Groottes tussenresultaten voor ratio {nrOfClauses/nrOfVars}")
        plt.legend()
        plt.xticks(range(1, 21, 2))
        plt.yscale('log')
        plt.savefig(f"figs/sizes/{vtree}/20_{nrOfVars}_{nrOfClauses}_{heuristics}_{operationStr}.png") #savefig moet blijkbaar voor show() komen
        plt.clf()
    #varcounts
    for nrOfClauses in range(int(nrOfVars*0.25), nrOfVars*5, int(nrOfVars*0.25)):
        filename = f"output/varCounts/{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt"
        with open(filename, 'r') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]
        for (index, line) in enumerate(lines):
            try:
                current_list = eval(line)
            except SyntaxError:
                print(f"Invalid list format in line: {line}")
            plt.plot(range(1, nrOfSdds), current_list, marker='o', \
                        linestyle='-', color = colors[index], label=getHeuristicName(heuristics[index]))
        plt.xlabel('Index tussenresultaat')
        plt.ylabel('aantal variabelen in tussenresultaat')
        plt.title(f"aantal vars per tussenresultaat voor ratio {nrOfClauses/nrOfVars}")
        plt.legend()
        plt.xticks(range(1, 21, 2))
        plt.savefig(f"figs/varCounts/{vtree}/20_{nrOfVars}_{nrOfClauses}_{heuristics}_{operationStr}.png") #savefig moet blijkbaar voor show() komen
        plt.clf()


def __main__():
    #heuristieken: VP_EL, VO, VP_KE, IVO_LR, IVO_RL, RANDOM
    heuristics = [RANDOM, VP_KE, VP_EL, IVO_LR, VO, IVO_RL]
    # heuristicsApply(heuristics, 16, "balanced")
    graphHeuristicApply(heuristics, 16, "balanced")
    #randomOrderMaxSizeVariation()
        
__main__()