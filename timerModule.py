from randomOrderApplier import RandomOrderApply
from randomOrderApplier import RANDOM, INVERSE_VAR_ORDER_LR, INVERSE_VAR_ORDER_RL, \
    SMALLEST_FIRST, VTREESPLIT, VTREESPLIT_WITH_SMALLEST_FIRST, VTREE_VARIABLE_ORDERING, \
    ELEMENT_UPPERBOUND, VTREESPLIT_WITH_EL_UPPERBOUND, heuristicDict
from randomOrderApplier import OR, AND

import timeit
import numpy
"""
voer dit uit voor de resultaten in een json file te bewaren
python3 bench.py -o bench.json

randomOrderCompTimeVariation:
    OR:
    -20 var -> met 2 clauses tot 100 clauses
    -10 of 20 sdd 
    AND: (ratio clause/var > 4.2 -> highly likely unsatisfaible)
    -20 var -> met 2 tot 10 clauses
    -10 sdd
"""

def addCounts(counts):
    prev = 0
    total = 0
    for i in counts:
        total += max(i - prev, 0)
        prev = i
    return total

def doCountingTest(nrOfIterations, randomApplier, operation):
    times = []
    totalNodes = []
    for _ in range(nrOfIterations):
        time = timeit.timeit(lambda: randomApplier.doHeuristicApply(RANDOM, operation), number = 1)
        times.append(time)
        counts = randomApplier.extractCounts()
        totalNodes.append(addCounts(counts))
    return times, totalNodes

def doRandomOrderTest(nrOfIterations, randomApplier, operation):
    times = []
    for _ in range(nrOfIterations):
        # sdds = randomApplier.loadBaseSdds()
        time = timeit.timeit(lambda: randomApplier.doHeuristicApply(RANDOM, operation), number = 1)
        times.append(time)
    return times

def countingVSTiming(operation):
    nrOfSdds=20
    nrOfVars=15
    nrOfIterationsPerSdd = 1000
    listNrOfClauses=list(tuple(range(5, int(nrOfVars*5), 5)))
    for nrOfClauses in listNrOfClauses:
        #print(nrOfClauses)
        randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type="balanced")
        times, counts = doCountingTest(nrOfIterationsPerSdd, randomApplier, operation)

        correlation_matrix = numpy.corrcoef(times, counts)
        correlation_coefficient = correlation_matrix[0, 1]
        print(f"Correlation Coefficient voor {nrOfClauses} clauses: {correlation_coefficient}")


def randomOrderCompTimeVariation(operation):
    nrOfSdds=20
    nrOfVars=16
    nrOfIterationsPerSdd = 10000
    listNrOfClauses=list(tuple(range(5, int(nrOfVars*5), 5)))
    operationStr = "OR" if operation == OR else "AND"
    with open(f"output/randomOrderCompTimeVariation_{nrOfSdds}_{nrOfVars}_{operationStr}.txt", 'w') as file:
        file.write(f"experiment: sdds: {nrOfSdds}, vars: {nrOfVars}, operation = {operationStr}" + '\n')
        for nrOfClauses in listNrOfClauses:
            print(nrOfClauses)
            randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type="balanced")
            times = doRandomOrderTest(nrOfIterationsPerSdd, randomApplier, operation)
            file.write(f"voor {nrOfClauses} clauses {times}\n")

def doHeuristicTest(heuristics, randomApplier, operation, overheadTime):
    timeHeuristics = []
    for heur in heuristics:
        if (overheadTime):
            timeHeuristics.append(timeit.timeit(lambda: randomApplier.doHeuristicApply(heur, operation), number = 1))
        else:
            (_, time) = randomApplier.doHeuristicApply(heur, operation, overheadTime)
            timeHeuristics.append(time)
    return timeHeuristics

def heuristicsApply(nrOfClauses, heuristics, operation, overheadTime):
    nrOfSdds=20
    nrOfVars=24
    iterations = 100
    vtree = "balanced"
    operationStr = "OR" if operation == OR else "AND"
    with open(f"output/heuristic/test_{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt", 'w') as file:
        file.write(f"experiment: sdds: {nrOfSdds}, vars: {nrOfVars}, operation = {operationStr}, vtree = {vtree}, heuristiek = {heuristics}" + '\n')
        heuristicsTimes = []
        randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type=vtree)
        for i in heuristics:
            heuristicsTimes.append([])
        for _ in range(iterations):
            randomApplier.renew()
            timeHeuristics = doHeuristicTest(heuristics, randomApplier, operation, overheadTime)
            for i in range(len(timeHeuristics)):
                heuristicsTimes[i].append(timeHeuristics[i])
        for i in range(len(heuristics)):
            file.write(f"heuristiek {heuristics[i]} times: {heuristicsTimes[i]}\n")

def diffSizesApply(heuristics, operation):
    nrOfSdds = 20
    nrOfVarsList = list(range(10, 32, 2))
    iterations = 1
    vtree = "balanced"
    operationStr = "OR" if operation == OR else "AND"
    for nrOfVars in nrOfVarsList:
        print("nrofVars = ", nrOfVars)
        nrOfClauses = round(1.8*nrOfVars)
        with open(f"output/diffSizes_{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt", 'w') as file:
            file.write(f"experiment: sdds: {nrOfSdds}, vars: {nrOfVars}, operation = {operationStr}, vtree = {vtree}, heuristiek = {heuristics}" + '\n')
            heuristicsTimes = []
            randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type=vtree)
            for i in heuristics:
                heuristicsTimes.append([])
            for _ in range(iterations):
                randomApplier.renew()
                timeHeuristics = doHeuristicTest(heuristics, randomApplier, operation, overheadTime=True)
                for i in range(len(timeHeuristics)):
                    heuristicsTimes[i].append(timeHeuristics[i])
            for i in range(len(heuristics)):
                file.write(f"heuristiek {heuristics[i]} times: {heuristicsTimes[i]}\n")
    

def __main__():
    #heuristieken: RANDOM, SMALLEST_FIRST, VTREESPLIT, VTREESPLIT_WITH_SMALLEST_FIRST, VTREE_VARIABLE_ORDERING, ELEMENT_UPPERBOUND
    heuristics = [VTREESPLIT_WITH_EL_UPPERBOUND, INVERSE_VAR_ORDER_RL]
    operation = OR 
    for i in range(int(24*0.5), 24*5, int(24*0.5)):
        print(f"nr of clauses = {i}")
        heuristicsApply(i, heuristics, operation, overheadTime=True) #false -> tijdsmeting zonder overhead
    # diffSizesApply(heuristics, operation)
    # countingVSTiming()
    #randomOrderCompTimeVariation()
    #print(times)
        
__main__()