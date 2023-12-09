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
        sdds = randomApplier.loadBaseSdds()
        time = timeit.timeit(lambda: randomApplier.doRandomApply(sdds), number = 1)
        randomApplier.collectGarbage()
        times.append(time)
    return times

def randomOrderCompTimeVariation():
    nrOfSdds=20
    nrOfVars=10
    operation="OR"
    listNrOfClauses=list(tuple(range(5, 50, 5)))
    allTimes = []
    with open(f"output/randomOrderCompTimeVariation_{nrOfSdds}_{nrOfVars}_{operation}_reverse.txt", 'w') as file:
        file.write(f"experiment: sdds: {nrOfSdds}, vars: {nrOfVars}, operation = {operation}" + '\n')
        for nrOfClauses in listNrOfClauses:
            print(nrOfClauses)
            randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, cnf3=True, operation = operation)
            times = doRandomOrderTest(100, randomApplier)
            file.write(f"voor {nrOfClauses} clauses {times}\n")

def doHeuristicTest(heur, randomApplier):
    sdds = randomApplier.loadBaseSdds()
    timeRandom = timeit.timeit(lambda: randomApplier.doHeuristicApply(sdds, heuristic = 99), number = 1)
    randomApplier.collectGarbage()

    sdds = randomApplier.loadBaseSdds()
    timeHeuristic = timeit.timeit(lambda: randomApplier.doHeuristicApply(sdds, heur), number = 1)
    randomApplier.collectGarbage()

    return (timeRandom, timeHeuristic)

def randomVsHeuristicApply():
    nrOfSdds=20
    nrOfVars=15
    nrOfClauses = 10
    operation="OR"
    heuristic = 1
    iterations = 1000

    with open(f"output/randomVsHeuristic_{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operation}_{heuristic}_2.txt", 'w') as file:
        file.write(f"experiment: sdds: {nrOfSdds}, vars: {nrOfVars}, operation = {operation}, heuristiek = {heuristic}" + '\n')
        randomTimes = []
        heuristicTimes = []
        for i in range(iterations):
            print(i)
            randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, cnf3=True, operation = operation)
            #randomApplier.minimize_final_vtree()
            (timeRandom, timeHeuristic) = doHeuristicTest(heuristic, randomApplier)
            randomTimes.append(timeRandom)
            heuristicTimes.append(timeHeuristic)
        file.write(f"random times: {randomTimes}\n")
        file.write(f"heuristiek {heuristic} times: {heuristicTimes}\n")

def __main__():
    randomVsHeuristicApply()
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