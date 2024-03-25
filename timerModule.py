from randomOrderApplier import RandomOrderApply
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
    timeRandom = timeit.timeit(lambda: randomApplier.doRandomApply(), number = 1)
    timeHeuristics = []
    for heur in heuristics:
        timeHeuristics.append(timeit.timeit(lambda: randomApplier.doHeuristicApply(heur), number = 1))
    return (timeRandom, timeHeuristics)

def randomVsHeuristicApply(nrOfClauses):
    nrOfSdds=20
    nrOfVars=16
    operation="OR"
    heuristics = [1, 2, 3, 4]
    iterations = 1000
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
            (timeRandom, timeHeuristics) = doHeuristicTest(heuristics, randomApplier)
            randomTimes.append(timeRandom)
            for i in range(len(timeHeuristics)):
                heuristicsTimes[i].append(timeHeuristics[i])
        file.write(f"random times: {randomTimes}\n")
        for i in range(len(heuristics)):
            file.write(f"heuristiek {heuristics[i]} times: {heuristicsTimes[i]}\n")

def __main__():
    # countingVSTiming()
    # for i in range(5, 70, 5):
    #     print(f"nr of clauses = {i}")
    #     randomVsHeuristicApply(i)
    randomOrderCompTimeVariation()
    #print(times)
        
__main__()