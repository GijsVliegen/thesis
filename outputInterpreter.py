import os
import statistics
from heuristicApplier import RANDOM
import numpy as np

#script voor postprocessing van alle resultaten van BCFormulaParser
#verschillende filters en combinaties van de resultaten zijn geimplementeerd

#berekent average results als meerdere iteraties zijn gedaan voor een formule
def resultsCombinerHeur(folderPath, heur, iters):
    totalTimes = 0
    noOHTimes = 0
    for i in range(iters):
        file = os.path.join(folderPath, f"{heur}_{i}.txt")
        try:
            with open(file, 'r') as file:
                line = file.readlines()[0][:-1]
                (totalTime, noOHTime) = line.split(" ")
                totalTimes += float(totalTime)
                noOHTimes += float(noOHTime)
        except FileNotFoundError:
            x = 5
    return (totalTimes/iters), (noOHTimes/iters)

nrOfHeurs = 4
heurNames = ["EL", "EL 2", "IVO", "IVO 2", "COMBO", "COMBO 2"]
def resultsCombiner(folderPath):
    heurs = [8, 7, 11]
    heurResults = []
    randomResults = []
    sigmaTotal, sigmaNoOH = 0,0
    iters = 11
    randomIters = 101
    for heur in heurs:
        totalTime, noOHTime = resultsCombinerHeur(folderPath, heur, iters)
        heurResults.append(totalTime)
        heurResults.append(noOHTime)

    for i in range(randomIters):
        file = os.path.join(folderPath, f"{RANDOM}_{i}.txt")
        try:
            with open(file, 'r') as file:
                line = file.readlines()[0][:-1]
                (totalTime, noOHTime) = line.split(" ")
                randomResults.append(float(totalTime))
                randomResults.append(float(noOHTime))
        except FileNotFoundError:
            x = 5

    if len(randomResults) >= 4:
        muTotal = statistics.mean(randomResults[::2])
        muNoOH = statistics.mean(randomResults[1::2])
        sigmaTotal = statistics.stdev(randomResults[::2])
        sigmaNoOH = statistics.stdev(randomResults[1::2])
        heurResults.append(muTotal)
        heurResults.append(muNoOH)
    return heurResults, sigmaTotal, sigmaNoOH

#outputfunction: telt hoevaak een bep. heuristiek in minimum tijd resulteert over alle formulas
def minCounter(results):
    minCounter = [0] * len(results[0])
    for result in results:
        if (len(result) == 0):
            continue
        minIndexTotal = result.index(min(result[::2]))
        minIndexNoOH = result.index(min(result[1::2]))
        minCounter[minIndexNoOH] += 1
        minCounter[minIndexTotal] += 1
    print(minCounter)

#outputfunction 
#   calculates compilationtimes for a formula, relative to the compilation time using Random heuristic, 
#   then calculates normal distribution properties of these relative compilationtimes over all formulas.
def relativeToRandomGauss(results):
    relativeLists = []
    for i in range(len(results[0])-2):
        relativeLists.append([])
    for result in results:
        for index in range(0, len(result)-2, 2):
            relativeLists[index].append(result[index]/result[-2])
            relativeLists[index+1].append(result[index+1]/result[-1])

    for heurList, heurName in zip(relativeLists, heurNames): 
        mu = statistics.mean(heurList)
        sigma = statistics.stdev(heurList)
        print(f"{heurName}: mu = {mu}, sigma = {sigma}")
    # return relativeLists

#outputfunction calculating average ZScores using the random times to guess a normal distribution of compilation times
def averageZScore(results, totalStdDev, noOHStdDev):
    relativeLists = []
    for i in range(len(results[0])-2):
        relativeLists.append([])
    for result, totalStd, noOHStd in zip(results, totalStdDev, noOHStdDev):
        if totalStd == 0:
            x = 5
        for index in range(0, len(result)-2, 2):
            relativeLists[index].append((result[index] - result[-2])/totalStd) #(i - mean)/std_dev
            relativeLists[index+1].append((result[index+1] - result[-1])/noOHStd)
    for heurList, heurName in zip(relativeLists, heurNames): 
        mu = statistics.mean(heurList)
        print(f"{heurName} average z-score: mu = {mu}")

#filters out low times
def noLowTimes(results, totalStds, noOHStds):
    print(f"nr of results = {len(results)}")
    for result, std, noOHStd in zip(results.copy(), totalStds.copy(), noOHStds.copy()):
        if len(result) == 0 or min(result) < 1:
            results.remove(result)
            totalStds.remove(std)
            noOHStds.remove(noOHStd)
    print(f"nr of results after filter = {len(results)}")
    return results, totalStds, noOHStds

#filters out results where results for some heuristics are missing
def clean(results, totalStds, noOHStds):
    print(f"nr of results = {len(results)}")
    for result, std, noOHStd in zip(results.copy(), totalStds.copy(), noOHStds.copy()):
        if len(result) < nrOfHeurs*2:
            results.remove(result)
            totalStds.remove(std)
            noOHStds.remove(noOHStd)
    print(f"nr of results after filter = {len(results)}")
    return results, totalStds, noOHStds

#iterates over all the folders (representing different formulas) combining results for each folder,
#   outputs information of results over all formulas 
def folderIterator(folderPath, interpretFunction, outputFunction, filter):
    # for root, dirs, files in os.walk(folderPath):
    #     allResults = []
    #     for dir in dirs:
    #         result = interpretFunction(os.path.join(folderPath, dir))
    #         allResults.append(result)
    #     outputFunction(allResults)
    allResults = []
    allTotalStd = []
    allNoOHStd = []
    for root, dirs, files in os.walk(folderPath):
        result, totalRandomStdDev, noOHRandomStdDev = interpretFunction(root)
        allResults.append(result)
        allTotalStd.append(totalRandomStdDev)
        allNoOHStd.append(noOHRandomStdDev)
    
    allResults, allTotalStd, allNoOHStd = filter(allResults, allTotalStd, allNoOHStd)
    # allTotalStd = [item for item in allTotalStd if item != 0]
    # allNoOHStd = [item for item in allNoOHStd if item != 0]


    outputFunction(allResults, allTotalStd, allNoOHStd)

# folderIterator("outputPaper", resultsCombiner, minCounter, clean)
# folderIterator("outputPaper", resultsCombiner, minCounter, noLowTimes)
# folderIterator("outputPaper", resultsCombiner, relativeToRandomGauss, clean)
# folderIterator("outputPaper", resultsCombiner, relativeToRandomGauss, noLowTimes)
folderIterator("outputPaper", resultsCombiner, averageZScore, clean)
folderIterator("outputPaper", resultsCombiner, averageZScore, noLowTimes)