import argparse
import matplotlib.pyplot as plt
import pyperf
import pylab
import os
import scipy.stats as stats
from heuristicApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, VP_ELVAR, ELVAR , \
    EL, heuristicDict, OR, AND

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
    try:
        list_str = line[start_pos:end_pos+1]
        if ',' in list_str:
            current_list = eval(list_str)
        else:
            list_str = line[start_pos+1:end_pos]
            current_list = list_str.split()
    except SyntaxError:
        print(f"Invalid list format in line: {line}")
    return current_list

def heuristicsPlot(heuristics, nrOfVars, vtree, operation):
    nrOfSdds=20
    overhead = True#False#True
    testName = "test" if overhead else "noOverhead"
    operationStr = "OR" if operation == OR else "AND"
    colors = ['red', 'blue', "green", "orange", "purple", "brown", "pink", "yellow"]
    nrOfClausesLists = list(range(int(nrOfVars/2), int(nrOfVars*5), int(nrOfVars/2)))
    for nrOfClauses in nrOfClausesLists:
        # {testName}_{nrOfSdds}_{nrOfVars}_{operationStr}_{vtree}_{heuristics}_{nrOfClauses}
        filename = f"output/heuristic/{testName}_{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt"
        with open(filename, 'r') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]
        ratio = nrOfClauses/nrOfVars
        for index, line in enumerate(lines):
            try:
                heuristicList = eval(line)
            except SyntaxError:
                print(f"Invalid list format in line: {line}")
            col = colors[index]
            counts, bins, _ = plt.hist(heuristicList, bins=20, edgecolor='black', alpha=0)  # Using alpha=0 makes bars invisible
            plt.plot(bins[:-1], counts, linestyle='-', color = col, marker='o', label=getHeuristicName(heuristics[index])) #lijn tussen de toppen van de histogram
        plt.xlabel('tijd (s)')
        plt.ylabel('aantal compilaties')
        plt.xscale('log')
        titleOperation = "disjunctie" if operation == OR else "conjunctie"
        plt.title(f"Compilatietijd {titleOperation} voor r = {ratio}")
        plt.legend()
        local_file_path = f"figs/heuristics/{vtree}/{testName}_{nrOfSdds}_{nrOfVars}_{operationStr}_{heuristics}_{nrOfClauses}.png"
        fullPath = os.path.join("", local_file_path)
        os.makedirs(os.path.dirname(fullPath), exist_ok=True)
        plt.savefig(local_file_path)
        plt.clf() #clear

def otherMetricsPlot(heuristics, nrOfVars, vtree, operation):
    nrOfSdds=20
    operationStr = "OR" if operation == OR else "AND"
    overhead = True#False#True
    testName = "test" if overhead else "noOverhead"
    colors = ['red', 'blue', "green", "orange", "purple", "brown", "yellow", "pink"]
    #sizes
    metrics = ["sizes", "varCounts", "depth"]
    ylabels = ['Grootte van tussenresultaat', 'aantal variabelen in tussenresultaat', 'hoogte van tussenresultaat']
    titles = ["groottes tussenresultaten voor ratio", "aantal vars per tussenresultaat voor ratio", "diepte tussenresultaten voor ratio"]
    yscale = ['log', 'linear', 'linear']
    for (i, metric) in enumerate(metrics):
        for nrOfClauses in range(int(nrOfVars*0.5), nrOfVars*5, int(nrOfVars*0.5)):
            # {testName}_{nrOfSdds}_{nrOfVars}_{operationStr}_{vtree}_{heuristics}_{nrOfClauses}
            filename = f"output/{metric}/{testName}_{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{operationStr}_{vtree}_{heuristics}.txt"
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
            plt.ylabel(ylabels[i])
            titleOperation = "Disjunctie" if operation == OR else "Conjunctie"
            plt.title(titleOperation + ": " + titles[i] + " " + str(nrOfClauses/nrOfVars))
            plt.legend()
            plt.xticks(range(1, 21, 2))
            plt.yscale(yscale[i])
            local_file_path = f"figs/{metric}/{vtree}/{testName}_{nrOfSdds}_{nrOfVars}_{operationStr}_{heuristics}_{nrOfClauses}.png"
            fullPath = os.path.join("", local_file_path)
            os.makedirs(os.path.dirname(fullPath), exist_ok=True)   
            plt.savefig(local_file_path) #savefig moet blijkbaar voor show() komen
            plt.clf()

def __main__():
    heuristics = [99, 4, 6, 7, 3, 8]
    nrOfVars = 28
    vtree = "balanced"
    operation = OR
    heuristicsPlot(heuristics, nrOfVars, vtree, operation) 
    otherMetricsPlot(heuristics, nrOfVars, vtree, operation)
    operation = AND
    heuristicsPlot(heuristics, nrOfVars, vtree, operation) 
    otherMetricsPlot(heuristics, nrOfVars, vtree, operation)
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
