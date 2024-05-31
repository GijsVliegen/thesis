import argparse
import matplotlib.pyplot as plt
import pyperf
import pylab
import os
import scipy.stats as stats
import numpy as np
from heuristicApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, VP_ELVAR, ELVAR , \
    EL, heuristicDict, OR, AND, VP_EL, IVO_RL_EL, IVO_RL_EL_Size

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
        binIndices = []
        for i in range(len(bins)-1):
            binIndices.append((bins[i+1]+bins[i]) / 2)
        plt.plot(binIndices, counts, linestyle='-', marker='o')
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

def binplotter(ax1, filename, heuristic, indexCounter, colors):
    lines = []
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
    lines = [line.strip() for line in lines]
    col = colors[indexCounter]
    for index, line in enumerate(lines):
        try:
            heuristicList = eval(line)
            counts, bins, _ = ax1.hist(heuristicList, bins=20, edgecolor='black', alpha=0)  # Using alpha=0 makes bars invisible
            ax1.plot(bins[:-1], counts, linestyle='-', color = col, marker='o', label=getHeuristicName(heuristic))
        except SyntaxError:
            print(f"Invalid list format in line: {line}")


def boxplotter(ax1, filename, indexCounter, colors):
    lines = []
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
    lines = [line.strip() for line in lines]
    for index, line in enumerate(lines):
        try:
            heuristicList = eval(line)
            if len(heuristicList) == 1:
                heuristicList = heuristicList[0]
            print(f"aantal iteraties = {len(heuristicList)}")
            box = ax1.boxplot(heuristicList, positions = [indexCounter], patch_artist=True, widths = 0.6)
            color = colors[indexCounter]
            for patch in box['boxes']:
                patch.set_facecolor(color)
            for median in box['medians']: #gemiddelde
                median.set_color('black')

            ax1.axhline(y=np.mean(heuristicList), xmin=indexCounter/9+0.01, xmax=indexCounter/9 + 1/9 -0.01, color='black', linestyle='-')
        except SyntaxError:
            print(f"Invalid list format in line: {line}")

def heuristicsPlot(heuristics, nrOfVars, vtree, operation):
    operationStr = "OR" if operation == OR else "AND"
    colors = ['red', 'lightblue', "green", "orange", "purple", "brown", "pink", "yellow", "blue", "lightgreen"]
    nrOfClausesLists = list(range(int(nrOfVars/2), int(nrOfVars*5), int(nrOfVars/2)))
    for nrOfClauses in nrOfClausesLists:
        fig, ax1 = plt.subplots()

        indexCounter = 0
        for heuristic in heuristics:
            filename = f"output/heuristic/test_20_{nrOfVars}_{operationStr}_{vtree}_{[heuristic]}_{nrOfClauses}.txt"
            boxplotter(ax1, filename, indexCounter, colors)
            # binplotter(ax1, nrOfVars, operationStr, vtree, heuristic, nrOfClauses, indexCounter, colors)
            indexCounter += 1
        for heur in [VP_EL, IVO_RL_EL]:
            filename = f"output/heuristic/noOverhead_20_{nrOfVars}_{operationStr}_{vtree}_{[heur]}_{nrOfClauses}.txt"
            boxplotter(ax1, filename, indexCounter, colors)
            # binplotter(ax1, nrOfVars, operationStr, vtree, VP_EL, nrOfClauses, indexCounter, colors, noOverhead = True)
            indexCounter += 1

        ratio = nrOfClauses/nrOfVars
        titleOperation = "Disjunctie" if operation == OR else "Conjunctie"
        plt.title(f"{titleOperation}: compilatietijd voor r = {ratio}")
        plt.xticks(list(range(indexCounter)), list(map(getHeuristicName, heuristics)) + ["VP + EL 2", "BU-EL 2"])
        plt.xlabel('heuristiek')
        plt.ylabel('tijd (s)')
        plt.yscale("log")

        ax2 = ax1.twinx()
        y_min, y_max = ax1.get_ylim()  # Get the limits from the left y-axis
        ax2.set_ylim(y_min, y_max)  # Set the same limits for the right y-axis
        # Hide the spines between ax1 and ax2
        ax1.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.yaxis.tick_right()
        ax2.set_yscale("log")

        local_file_path = f"figs/heuristics/{vtree}/test_20_{nrOfVars}_{operationStr}_{heuristics+[10]}_{nrOfClauses}.png"
        fullPath = os.path.join("", local_file_path)
        os.makedirs(os.path.dirname(fullPath), exist_ok=True)
        plt.savefig(local_file_path)
        plt.clf() #clear

def plotter(filename, heuristic, indexCounter, colors, alpha = 1):
    # 
    lines = []
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
    lines = [line.strip() for line in lines]
    for (index, line) in enumerate(lines):
        try:
            current_list = eval(line)
        except SyntaxError:
            print(f"Invalid list format in line: {line}")
        if heuristic == RANDOM:
            plt.plot(range(1, 20), current_list, marker='o', \
                        linestyle='-', color = colors[indexCounter], alpha = alpha)
        else: 
            plt.plot(range(1, 20), current_list, marker='o', \
                        linestyle='-', color = colors[indexCounter], label=getHeuristicName(heuristic))

def horizontalLinePlotter(ax1, filename, heuristic, indexCounter, colors, noOverhead=True):
    lines = []
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
    lines = [line.strip() for line in lines]
    # print(f"length should be one and is = {len(lines)}")
    for (index, line) in enumerate(lines):
        try:
            current_list = eval(line)
        except SyntaxError:
            print(f"Invalid list format in line: {line}")
        if noOverhead:
            ax1.axhline(y=current_list[0], label = getHeuristicName(heuristic), color = colors[indexCounter])
        else:
            ax1.axhline(y=current_list[0], label = "VP + EL 2", color = colors[indexCounter])


def otherMetricsPlot(heuristics, nrOfVars, vtree, operation):
    nrOfSdds=20
    operationStr = "OR" if operation == OR else "AND"
    overhead = True#False#True
    testName = "test" if overhead else "noOverhead"
    colors = ['red', 'lightblue', "green", "orange", "purple", "brown", "yellow", "pink"]
    #sizes
    metrics = ["sizes", "varCounts", "depth"]
    ylabels = ['Grootte van tussenresultaat', 'aantal variabelen in tussenresultaat', 'hoogte van tussenresultaat']
    titles = ["groottes tussenresultaten voor r =", "aantal vars per tussenresultaat voor r =", "diepte tussenresultaten voor r ="]
    yscale = ['log', 'linear', 'linear']
    for (i, metric) in enumerate(metrics):
        for nrOfClauses in range(int(nrOfVars*0.5), nrOfVars*5, int(nrOfVars*0.5)):
            indexCounter = 0
            for heuristic in heuristics:
                filename = f"output/{metric}/test_20_{nrOfVars}_{operationStr}_{vtree}_{[heuristic]}_{nrOfClauses}.txt"
                plotter(filename, heuristic, indexCounter, colors)
                indexCounter += 1

            plt.xlabel('Index tussenresultaat')
            plt.ylabel(ylabels[i])
            titleOperation = "Disjunctie" if operation == OR else "Conjunctie"
            plt.title(titleOperation + ": " + titles[i] + " " + str(nrOfClauses/nrOfVars))
            plt.legend()
            plt.xticks(range(1, 21, 2))
            plt.yscale(yscale[i])
            local_file_path = f"figs/{metric}/{vtree}/{testName}_{nrOfSdds}_{nrOfVars}_{operationStr}_{heuristics+[10]}_{nrOfClauses}.png"
            fullPath = os.path.join("", local_file_path)
            os.makedirs(os.path.dirname(fullPath), exist_ok=True)   
            plt.savefig(local_file_path) #savefig moet blijkbaar voor show() komen
            plt.clf()

def randomRatiosPlot(heuristics, nrOfVars, vtree, operation):
    nrOfSdds=20
    operationStr = "OR" if operation == OR else "AND"
    overhead = True#False#True
    testName = "test" if overhead else "noOverhead"
    colors = ['red', 'lightblue', "green", "orange", "purple", "brown", "yellow", "pink"]
    #sizes
    metrics = ["sizes", "varCounts", "depth"]
    ylabels = ['Grootte van tussenresultaat', 'aantal variabelen in tussenresultaat', 'hoogte van tussenresultaat']
    titles = ["groottes tussenresultaten voor r =", "aantal vars per tussenresultaat voor r =", "diepte tussenresultaten voor r ="]
    yscale = ['log', 'linear', 'linear']

    for (i, metric) in enumerate(metrics):
        indexCounter = 0
        for heuristic in heuristics:
            filename = f"output/randomRatios/{metric}/test_20_{nrOfVars}_{operationStr}_{vtree}_{[heuristic]}.txt"
            plotter(filename, heuristic, indexCounter, colors)
            indexCounter += 1

        plt.xlabel('Index tussenresultaat')
        plt.ylabel(ylabels[i])
        titleOperation = "Disjunctie" if operation == OR else "Conjunctie"
        plt.title(titleOperation + ": " + titles[i])
        plt.legend()
        plt.xticks(range(1, 21, 2))
        plt.yscale(yscale[i])
        local_file_path = f"figs/randomRatios/{metric}/{vtree}/{testName}_{nrOfSdds}_{nrOfVars}_{operationStr}_{heuristics+[10]}.png"
        fullPath = os.path.join("", local_file_path)
        os.makedirs(os.path.dirname(fullPath), exist_ok=True)   
        plt.savefig(local_file_path) #savefig moet blijkbaar voor show() komen
        plt.clf()
    
    operationStr = "OR" if operation == OR else "AND"
    colors = ['red', 'lightblue', "green", "orange", "purple", "brown", "pink", "yellow"]
    fig, ax1 = plt.subplots()

    indexCounter = 0
    for heuristic in heuristics:
        filename = f"output/randomRatios/heuristic/test_20_{nrOfVars}_{operationStr}_{vtree}_{[heuristic]}.txt"
        # boxplotter(ax1, filename, indexCounter, colors)
        binplotter(ax1, filename, heuristic, indexCounter, colors)
        indexCounter += 1
    filename = f"output/randomRatios/heuristic/noOverhead_20_{nrOfVars}_{operationStr}_{vtree}_{[VP_EL]}.txt"
    # boxplotter(ax1, filename, indexCounter, colors)
    binplotter(ax1, filename, heuristic, indexCounter, colors)
    indexCounter += 1
    
    titleOperation = "Disjunctie" if operation == OR else "Conjunctie"
    plt.title(f"{titleOperation}: compilatietijd")
    
    #binplots
    plt.xscale("log")
    plt.xlabel("tijd (s)")
    plt.ylabel("aantal iteraties")
    
    #boxplots
    # plt.xticks(list(range(indexCounter)), list(map(getHeuristicName, heuristics)) + ["VP + EL 2"])
    # plt.xlabel('heuristiek')
    # plt.ylabel('tijd (s)')
    # plt.yscale("log")
    # ax2 = ax1.twinx()
    # y_min, y_max = ax1.get_ylim()  # Get the limits from the left y-axis
    # ax2.set_ylim(y_min, y_max)  # Set the same limits for the right y-axis
    # # Hide the spines between ax1 and ax2
    # ax1.spines['right'].set_visible(False)
    # ax2.spines['left'].set_visible(False)
    # ax2.yaxis.tick_right()
    # ax2.set_yscale("log")

    local_file_path = f"figs/randomRatios/heuristics/{vtree}/test_20_{nrOfVars}_{operationStr}_{heuristics+[10]}.png"
    fullPath = os.path.join("", local_file_path)
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)
    plt.savefig(local_file_path)
    plt.clf() #clear

def randomVariationPlot(heuristics, nrOfVars, iteration, vtree, operation):
    nrOfSdds=20
    operationStr = "OR" if operation == OR else "AND"
    overhead = True#False#True
    testName = "test" if overhead else "noOverhead"
    colors = ['red', 'lightblue', "green", "orange", "purple", "brown", "yellow", "pink"]
    #sizes]
    
    indexCounter = 0
    filename = f"output/randomVariation/{iteration}/sizes/test_20_{nrOfVars}_{operationStr}_{vtree}.txt"
    plotter(filename, RANDOM, indexCounter, colors, alpha = 0.4)
    indexCounter += 1
    for heuristic in heuristics:
        filename = f"output/randomVariation/{iteration}/sizes/test_20_{nrOfVars}_{operationStr}_{vtree}_{[heuristic]}.txt"
        plotter(filename, heuristic, indexCounter, colors)
        indexCounter += 1

    plt.xlabel('Index tussenresultaat')
    plt.ylabel('Grootte van tussenresultaat')
    titleOperation = "Disjunctie" if operation == OR else "Conjunctie"
    plt.title(titleOperation + ": variatie groottes tussenresultaten")
    plt.legend()
    plt.xticks(range(1, 21, 2))
    plt.yscale("log")
    local_file_path = f"figs/randomVariation/{iteration}/sizes/{vtree}/{testName}_{nrOfSdds}_{nrOfVars}_{operationStr}_{heuristics+[10]}.png"
    fullPath = os.path.join("", local_file_path)
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)   
    plt.savefig(local_file_path) #savefig moet blijkbaar voor show() komen
    plt.clf()
    
    operationStr = "OR" if operation == OR else "AND"
    colors = ['red', 'lightblue', "green", "orange", "purple", "brown", "pink", "yellow"]

    indexCounter = 0
    filename = f"output/randomVariation/{iteration}/heuristic/test_20_{nrOfVars}_{operationStr}_{vtree}.txt"

    randomTimesList = getList(filename)
    randomTimesList.sort()
    plt.plot(randomTimesList, linestyle='-', color = colors[0], marker='o', label=getHeuristicName(RANDOM))

    indexCounter += 1
    for heuristic in heuristics:
        filename = f"output/randomVariation/{iteration}/heuristic/test_20_{nrOfVars}_{operationStr}_{vtree}_{[heuristic]}.txt"
        # boxplotter(ax1, filename, indexCounter, colors)
        horizontalLinePlotter(plt, filename, heuristic, indexCounter, colors)
        indexCounter += 1
    if (VP_EL in heuristics):
        filename = f"output/randomVariation/{iteration}/heuristic/noOverhead_20_{nrOfVars}_{operationStr}_{vtree}_{[VP_EL]}.txt"
        # boxplotter(ax1, filename, indexCounter, colors)
        horizontalLinePlotter(plt, filename, VP_EL, indexCounter, colors, noOverhead=False)
        indexCounter += 1
    
    titleOperation = "Disjunctie" if operation == OR else "Conjunctie"
    plt.title(f"Disjunctie: compilatietijd")
    plt.legend()
    #binplots
    # plt.yscale("log")
    plt.ylabel("tijd (s)")
    plt.xlabel("resultaat nr")

    local_file_path = f"figs/randomVariation/{iteration}/heuristics/{vtree}/test_20_{nrOfVars}_{operationStr}_{heuristics+[10]}.png"
    fullPath = os.path.join("", local_file_path)
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)
    plt.savefig(local_file_path)
    plt.clf() #clear

def getList(filename):
    lines = []
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        pass
        # print(f"Error: The file '{filename}' does not exist.")
    lines = [line.strip() for line in lines]
    current_list = []
    for (index, line) in enumerate(lines):
        try:
            current_list = eval(line)
        except SyntaxError:
            print(f"Invalid list format in line: {line}")
    return current_list

def randomRatioVariationStats(heuristics, nrOfVars, iteration, vtree, operation, ratios):

    operationStr = "OR" if operation == OR else "AND"
    overhead = True#False#True
    
    heuristicIndices = []
    times = []
    filename = f"output/randomVariation/{iteration}/heuristic/test_20_{nrOfVars}_{operationStr}_{vtree}.txt"
    randomTimes = getList(filename)
    randomTimes.sort()
    for heuristic in heuristics:
        filename = f"output/randomVariation/{iteration}/heuristic/test_20_{nrOfVars}_{operationStr}_{vtree}_{[heuristic]}.txt"
        heuristicTimes = getList(filename)
        for i in heuristicTimes:
            times.append(i)
            index = 0
            while index < len(randomTimes) and i > randomTimes[index]:
                index += 1
            heuristicIndices.append(index)
    filename = f"output/randomVariation/{iteration}/heuristic/noOverhead_20_{nrOfVars}_{operationStr}_{vtree}_{[VP_EL]}.txt"
    heuristicTimes = getList(filename)

    combinedHeur = IVO_RL_EL #IVO_RL_EL_Size

    for i in heuristicTimes:
        times.append(i)
        index = 0
        while index < len(randomTimes) and i > randomTimes[index]:
            index += 1
        heuristicIndices.append(index)
    for ratio in ratios:
        filename = f"output/randomVariation/{iteration}/heuristic/test_20_{nrOfVars}_{operationStr}_{vtree}_{[combinedHeur]}_{ratio}.txt"
        heuristicTimes = getList(filename)
        for i in heuristicTimes:
            times.append(i)
            index = 0
            while index < len(randomTimes) and i > randomTimes[index]:
                index += 1
            heuristicIndices.append(index)
        filename = f"output/randomVariation/{iteration}/heuristic/noOverhead_20_{nrOfVars}_{operationStr}_{vtree}_{[combinedHeur]}_{ratio}.txt"
        heuristicTimes = getList(filename)
        for i in heuristicTimes:
            times.append(i)
            index = 0
            while index < len(randomTimes) and i > randomTimes[index]:
                index += 1
            heuristicIndices.append(index)
    return heuristicIndices, times
    


def __main__():
    heuristics = [99, VO, IVO_LR, IVO_RL, VP_KE, VP_EL, IVO_RL_EL]
    nrOfVars = 10
    vtree = "left"

    operation = OR
    # heuristicsPlot(heuristics, nrOfVars, vtree, operation) 
    # otherMetricsPlot(heuristics, nrOfVars, vtree, operation)
    # randomRatiosPlot(heuristics, nrOfVars, vtree, operation)

    operation = AND
    # heuristicsPlot(heuristics, nrOfVars, vtree, operation) 
    # otherMetricsPlot(heuristics, nrOfVars, vtree, operation)
    # randomRatiosPlot(heuristics, nrOfVars, vtree, operation)

    nrOfIters = 100
    totalStats = [0]*20
    totalTimes = [0]*20
    for iter in range(nrOfIters):
        # randomVariationPlot([], nrOfVars, iter, vtree, AND)
        heuristics = [4, 6, 7, 3, 8]
        ratios = [0.7]
        # ratios = [10000, 33000, 100000]
        # randomVariationPlot(heuristics, nrOfVars, iter, vtree, AND)
        stats, times = randomRatioVariationStats(heuristics, nrOfVars, iter, vtree, AND, ratios)
        #right + size: [41.48, 55.48, 50.27, 49.61, 60.18, 12.97, 55.8, 31.63
        #balanced + size: [33.3, 14.44, 15.26, 13.68, 30.97, 27.98, 24.93, 22.86
        #balanced + varratio: [33.3, 14.44, 15.26, 13.68, 30.97, 27.98, 28.01, 24.99
        #right + varratio: [41.48, 55.48, 50.27, 49.61, 60.18, 12.97, 61.9, 27.94,
        #left + varratio: [8.24, 5.78, 26.22, 26.24, 14.58, 13.89, 
        if stats[0] == min(stats):
            stringg = "\\textbf{" + f"{stats[0]}" + "}"
        else:
            stringg = f"{stats[0]}"
        for i in stats[1:]:
            stringg += " & "
            if i == min(stats):
                stringg += "\\textbf{" + f"{i}" + "}"
            else:
                stringg += f"{i}"
        stringg += " \\\\"
        print(stringg)

        # print(f"{iter}: {stats}")
        for i in range(len(stats)):
            totalStats[i] += stats[i]
            totalTimes[i] += times[i]
    for i in range(len(totalStats)):
        totalStats[i] /= nrOfIters
    print(totalStats)
    print(totalTimes)


__main__()

