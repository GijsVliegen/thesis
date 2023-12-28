from randomOrderApplier import RandomOrderApply
import timeit
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

def doRandomOrderTest(nrOfIterations, randomApplier):
    times = []
    for i in range(nrOfIterations):
        # sdds = randomApplier.loadBaseSdds()
        time = timeit.timeit(lambda: randomApplier.doRandomApply(), number = 1)
        times.append(time)
    return times

def randomOrderCompTimeVariation():
    nrOfSdds=20
    nrOfVars=20
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
    nrOfVars=15
    operation="OR"
    heuristics = [1, 2, 3, 4]
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
            print(i)
            randomApplier.renew()
            (timeRandom, timeHeuristics) = doHeuristicTest(heuristics, randomApplier)
            randomTimes.append(timeRandom)
            for i in range(len(timeHeuristics)):
                heuristicsTimes[i].append(timeHeuristics[i])
        file.write(f"random times: {randomTimes}\n")
        for i in range(len(heuristics)):
            file.write(f"heuristiek {heuristics[i]} times: {heuristicsTimes[i]}\n")

def __main__():
    randomVsHeuristicApply(5)
    randomVsHeuristicApply(10)
    randomVsHeuristicApply(25)
    randomVsHeuristicApply(40)
    #randomOrderCompTimeVariation()
    #print(times)
    
    #runner = pyperf.Runner(processes=1, loops = 1)
    #for nrOfClauses in listNrOfClauses:

        #with RandomApply(nrOfSdds, nrOfVars, nrOfClauses, cnf3=True, operation="OR") as randomApplier:
            #randomApplier.doRandomApply()
            #runner.bench_func(name=f'random apply ordering {nrOfSdds} {nrOfVars} {nrOfClauses}', func=randomApplier.doRandomApply)
    
        #result = runner.timeit(name="random apply ordering",
            #stmt="doRandomApply()",
            #setup="from randomOrderCompTimeVariation import doRandomApply")
        #result = runner.timeit(name="random apply ordering",
            #stmt="doRandomApply()",
            #setup="")
        #runner._display_result

    """print("Mean time: ", result.mean)
    print("Standard deviation: ", result.stdev)
    print("Min time: ", result.min)
    print("Max time: ", result.max)
    print("Number of loops: ", result.loops)
    print("Inner loops: ", result.inner_loops)"""
    """
    # Plot the range of integers for each key
    plt.plot(range(nrOfIterations), results, 'o', label=i) 

    # Add labels and a legend
    plt.yscale("log")
    plt.xlabel('try')
    plt.ylabel('total comp time')

    # Show the plot
    plt.show()
    plt.savefig(f"results/randomOrderCompTimeVariation{operation}.png")
"""
__main__()