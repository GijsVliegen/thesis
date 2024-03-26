import argparse
import matplotlib.pyplot as plt
import pyperf
import pylab
import scipy.stats as stats

def randomOrderVariancePlot():
    filename = "output/randomOrderCompTimeVariation_20_15_OR.txt"
    with open(filename, 'r') as file:
        # Read lines from the file
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    lists = []
    for (index, line) in enumerate(lines[1:]):
        start_pos = line.find('[')
        end_pos = line.find(']')
        list_str = line[start_pos:end_pos+1]
        try:
            current_list = eval(list_str)
        except SyntaxError:
            print(f"Invalid list format in line: {line}")

        counts, bins, _ = plt.hist(current_list, bins=30, edgecolor='black', alpha=0)  # Using alpha=0 makes bars invisible
        plt.plot(bins[:-1], counts, linestyle='-', marker='o', label=f"{index * 5} clausen") #lijn tussen de toppen van de histogram
        plt.show()
        #nrOfClausesList.append(int(line[:start_pos].split(" ")[1]))

    plt.xlabel('tijd (in s)')
    plt.ylabel('aantal compilaties')
    plt.title("Variatie in compilatietijd bij willekeurige apply ordening")
    plt.yscale('log')
    plt.legend()
    plt.savefig("randomOrderVariation.png") #savefig moet blijkbaar voor show() komen

def randomOrderPlot():
    filename = "output/randomOrderCompTimeVariation_20_15_OR.txt"
    with open(filename, 'r') as file:
        # Read lines from the file
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    lists = []
    for line in lines[1:]:
        start_pos = line.find('[')
        end_pos = line.find(']')
        list_str = line[start_pos:end_pos+1]
        try:
            current_list = eval(list_str)
        except SyntaxError:
            print(f"Invalid list format in line: {line}")

        #nrOfClausesList.append(int(line[:start_pos].split(" ")[1]))
        current_list = sorted(current_list)#[5:-5] #5 grootste en kleinste elementen weglaten om eventuele foute uitschieters weg te laten
        lists.append(current_list)
    plotMaxMinAverageList(lists)

    plt.xlabel('#clausen per cnf')
    plt.ylabel('tijd (in s)')
    plt.title("Variatie in compilatietijd bij willekeurige apply ordening")
    plt.yscale('log')
    plt.legend()
    plt.savefig("randomOrderVariation.png") #savefig moet blijkbaar voor show() komen

def plotMaxMinAverageList(lists):
    averageList = []
    maxList = []
    minList = []
    nrOfVars = 15
    listNrOfClauses=list(tuple(range(5, int(nrOfVars*5), 5)))
    for oneList in lists:        
        max = 0
        min = 99999
        sum = 0
        for i in oneList:
            if i > max:
                max = i
            if i < min:
                min = i
            sum += i
        averageList.append(sum/len(oneList))
        maxList.append(max)
        minList.append(min)
    plt.plot(listNrOfClauses, minList, label='min')
    plt.plot(listNrOfClauses, averageList, label='average')
    plt.plot(listNrOfClauses, maxList, label='max')

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
    filename = "output/randomVsHeuristic_20_16_5_1_OR_[99, 3, 4, 5].txt"
    heuristiekenIntList = getListFromLine(filename)
    heuristieken = []
    for heuristiekInt in heuristiekenIntList:
        variable_name = [name for name, value in locals().items() if value is heuristiekInt][0]
        heuristieken.append(variable_name) #haalt namen eruit ipv getallen voor heuristieken

    with open(filename, 'r') as file:
        # Read lines from the file
        lines = file.readlines()
    lines = [line.strip() for line in lines]
        
    #randomList = getListFromLine(lines[1])
    #plt.hist(randomList, bins=100, alpha=0.5, label='random')
    diff = []
    for index in range(len(lines[1:])):
        heuristiek = heuristieken[index]
        heuristicList = getListFromLine(lines[1 + index])
        #oneDiff = [heur/rand for (rand, heur) in zip(randomList, heuristicList)]
        #plt.plot(heuristicList, label = f"heur {heuristiek}")
        #plt.hist(oneDiff, bins = 100, alpha = 0.5, label = f"diff heur {heuristiek}")
        #plt.boxplot(oneDiff, positions = [heuristiek], widths=.8)
        # plt.hist(heuristicList, bins=100, alpha=0.5, label=f"heur {heuristiek}")
        counts, bins, _ = plt.hist(heuristicList, bins=30, edgecolor='black', alpha=0)  # Using alpha=0 makes bars invisible
        plt.plot(bins[:-1], counts, linestyle='-', marker='o', label=f"heur {heuristiek}") #lijn tussen de toppen van de histogram

    #plt.plot(randomList, label='random')
    #plt.plot(heuristicList, label='heuristic')
    plt.xlabel('tijd (s)')
    plt.ylabel('aantal compilaties')
    plt.title("compilatietijd bij heuristieken")
    plt.legend()
    plt.savefig("heuristieken results boxplot.png")

def __main__():
    heuristicsPlot() 
    #randomOrderPlot()
    #randomOrderVariancePlot()
    plt.show()
# Show the plot

__main__()

"""
suite = pyperf.BenchmarkSuite.load(filename)
for bench in suite.get_benchmarks():
    print(bench.get_name())
    nrOfClauses = int(bench.get_name().split(" ")[-1])
    values = bench.get_values()
    values = sorted(values)
    plt.boxplot(values, positions = [nrOfClauses], widths=1)"""