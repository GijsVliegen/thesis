import argparse
import matplotlib.pyplot as plt
import pyperf
import pylab
import scipy.stats as stats
from randomOrderApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, \
    EL, heuristicDict

def getHeuristicName(heuristicInt):
    return heuristicDict[heuristicInt]

def randomOrderPlot():
    nrOfVars = 15
    operation = "OR"
    vtree = "balanced"
    filename = f"output/randomOrderCompTimeVariation_20_{nrOfVars}_{operation}.txt"
    with open(filename, 'r') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    nrOfClausesList = list(range(5, 80, 5))
    for (index, line) in enumerate(lines[1:]):
        lister = getListFromLine(line)
        nrOfClauses = nrOfClausesList[index]
        ratio = nrOfClauses/nrOfVars
        #sort(list) #[5:-5] #5 grootste en kleinste elementen weglaten om eventuele foute uitschieters weg te laten
        counts, bins, _ = plt.hist(lister, bins=100, edgecolor='black', alpha=0)  # Using alpha=0 makes bars invisible
        plt.plot(bins[:-1], counts[:], linestyle='-', marker='o') #lijn tussen de toppen van de histogram
        plt.xlabel('tijd (in s)')
        plt.ylabel('aantal compilaties')
        plt.title(f"Variatie in compilatietijd voor r = {ratio}")
        plt.yscale('log')
        plt.savefig(f"figs/randomVariation/randomOrder_20_{nrOfVars}_{nrOfClauses}_{operation}.png") #savefig moet blijkbaar voor show() komen
        plt.clf()

def getListFromLine(line):
    start_pos = line.find('[')
    end_pos = line.find(']')
    list_str = line[start_pos:end_pos+1]
    try:
        current_list = eval(list_str)
    except SyntaxError:
        print(f"Invalid list format in line: {line}")
    return current_list

def heuristicsPlot():
    vtree = "balanced"
    heuristieken = "[99, 3, 8, 6, 4, 7]"
    overhead = False
    testName = "test" if overhead else "noOverhead"
    nrOfVars = 20
    operation = "OR"
    colors = ['red', 'blue', "green", "orange", "purple", "brown", "yellow", "pink"]
    nrOfClausesLists = list(range(int(nrOfVars/4), int(nrOfVars*1.25), int(nrOfVars*0.25)))
    #nrOfClausesLists = list(range(int(nrOfVars/2), int(nrOfVars*5), int(nrOfVars/2)))
    for nrOfClauses in nrOfClausesLists:
        filename = f"output/heuristic/{testName}_20_{nrOfVars}_{nrOfClauses}_{operation}_{vtree}_{heuristieken}.txt"
        heuristieken = getListFromLine(filename)
        with open(filename, 'r') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]
        ratio = nrOfClauses/nrOfVars
        for index in range(len(lines[1:])):
            heuristiek = heuristieken[index]
            heuristicList = getListFromLine(lines[1 + index])
            col = colors[index]
            counts, bins, _ = plt.hist(heuristicList, bins=30, edgecolor='black', alpha=0)  # Using alpha=0 makes bars invisible
            plt.plot(bins[:-10], counts[:-9], linestyle='-', color = col, marker='o', label=getHeuristicName(heuristiek)) #lijn tussen de toppen van de histogram
        plt.xlabel('tijd (s)')
        plt.ylabel('aantal compilaties')
        plt.xscale('log')
        plt.title(f"Compilatietijd voor r = {ratio}")
        plt.legend()
        plt.savefig(f"figs/heuristics/{vtree}/{testName}_20_{nrOfVars}_{nrOfClauses}_{operation}_{vtree}_{heuristieken}.png")
        plt.clf() #clear

def __main__():
    heuristicsPlot() 
    # randomOrderPlot()
    #plt.show()

__main__()

# def plotMaxMinAverageList(lists):
#     averageList = []
#     maxList = []
#     minList = []
#     nrOfVars = 15
#     listNrOfClauses=list(tuple(range(5, int(nrOfVars*5), 5)))
#     for oneList in lists:        
#         max = 0
#         min = 99999
#         sum = 0
#         for i in oneList:
#             if i > max:
#                 max = i
#             if i < min:
#                 min = i
#             sum += i
#         averageList.append(sum/len(oneList))
#         maxList.append(max)
#         minList.append(min)
#     plt.plot(listNrOfClauses, minList, label='min')
#     plt.plot(listNrOfClauses, averageList, label='average')
#     plt.plot(listNrOfClauses, maxList, label='max')
