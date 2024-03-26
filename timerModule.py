from randomOrderApplier import RandomOrderApply
from randomOrderApplier import RANDOM, SMALLEST_FIRST, VTREESPLIT, VTREESPLIT_WITH_SMALLEST_FIRST, VTREE_VARIABLE_ORDERING, ELEMENT_UPPERBOUND
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

def doCountingTest(nrOfIterations, randomApplier):
    times = []
    totalNodes = []
    for i in range(nrOfIterations):
        time = timeit.timeit(lambda: randomApplier.doRandomApply(), number = 1)
        times.append(time)
        counts = randomApplier.extractCounts()
        totalNodes.append(addCounts(counts))
    return times, totalNodes

def doRandomOrderTest(nrOfIterations, randomApplier):
    times = []
    for i in range(nrOfIterations):
        # sdds = randomApplier.loadBaseSdds()
        time = timeit.timeit(lambda: randomApplier.doRandomApply(), number = 1)
        times.append(time)
    return times

def countingVSTiming():
    nrOfSdds=20
    nrOfVars=15
    nrOfIterationsPerSdd = 1000
    operation="OR"
    listNrOfClauses=list(tuple(range(5, int(nrOfVars*5), 5)))
    for nrOfClauses in listNrOfClauses:
        #print(nrOfClauses)
        randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, nrOfCnfs=1, cnf3=True, operation = operation)
        times, counts = doCountingTest(nrOfIterationsPerSdd, randomApplier)

        correlation_matrix = numpy.corrcoef(times, counts)
        correlation_coefficient = correlation_matrix[0, 1]
        print(f"Correlation Coefficient voor {nrOfClauses} clauses: {correlation_coefficient}")


def randomOrderCompTimeVariation():
    nrOfSdds=20
    nrOfVars=16
    nrOfIterationsPerSdd = 10000
    operation="OR"
    listNrOfClauses=list(tuple(range(5, int(nrOfVars*5), 5)))
    with open(f"output/randomOrderCompTimeVariation_{nrOfSdds}_{nrOfVars}_{operation}.txt", 'w') as file:
        file.write(f"experiment: sdds: {nrOfSdds}, vars: {nrOfVars}, operation = {operation}" + '\n')
        for nrOfClauses in listNrOfClauses:
            print(nrOfClauses)
            randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, nrOfCnfs=1, cnf3=True, operation = operation)
            times = doRandomOrderTest(nrOfIterationsPerSdd, randomApplier)
            file.write(f"voor {nrOfClauses} clauses {times}\n")

def doHeuristicTest(heuristics, randomApplier):
    timeHeuristics = []
    for heur in heuristics:
        timeHeuristics.append(timeit.timeit(lambda: randomApplier.doHeuristicApply(heur), number = 1))
    return timeHeuristics

def heuristicsApply(nrOfClauses, heuristics):
    nrOfSdds=20
    nrOfVars=16
    operation="OR"
    iterations = 100
    nrOfCnfs = 1
    with open(f"output/randomVsHeuristic_{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{nrOfCnfs}_{operation}_{heuristics}.txt", 'w') as file:
        file.write(f"experiment: sdds: {nrOfSdds}, vars: {nrOfVars}, operation = {operation}, heuristiek = {heuristics}" + '\n')
        randomTimes = []
        heuristicsTimes = []
        randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, nrOfCnfs, cnf3=True, operation = operation)
        for i in heuristics:
            heuristicsTimes.append([])
        for i in range(iterations):
            randomApplier.renew()
            timeHeuristics = doHeuristicTest(heuristics, randomApplier)
            for i in range(len(timeHeuristics)):
                heuristicsTimes[i].append(timeHeuristics[i])
        for i in range(len(heuristics)):
            file.write(f"heuristiek {heuristics[i]} times: {heuristicsTimes[i]}\n")

def __main__():
    #heuristieken: RANDOM, SMALLEST_FIRST, VTREESPLIT, VTREESPLIT_WITH_SMALLEST_FIRST, VTREE_VARIABLE_ORDERING, ELEMENT_UPPERBOUND
    heuristics = [RANDOM, VTREESPLIT_WITH_SMALLEST_FIRST, VTREE_VARIABLE_ORDERING, ELEMENT_UPPERBOUND]
    for i in range(5, 80, 5):
        print(f"nr of clauses = {i}")
        heuristicsApply(i, heuristics)
    # countingVSTiming()
    #randomOrderCompTimeVariation()
    #print(times)
        
__main__()