import argparse
import matplotlib.pyplot as plt
import pyperf
import pylab
import scipy.stats as stats

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

def heuristicVsRandomPlot():
    filename = "output/randomVsHeuristic_20_15_5_1_OR_[1, 2, 3, 4].txt"
    heuristiekenList = getListFromLine(filename)

    with open(filename, 'r') as file:
        # Read lines from the file
        lines = file.readlines()
    lines = [line.strip() for line in lines]
        
    randomList = getListFromLine(lines[1])
    #plt.hist(randomList, bins=100, alpha=0.5, label='random')
    diff = []
    for index in range(len(lines[2:])):
        heuristiek = heuristiekenList[index]
        heuristicList = getListFromLine(lines[2 + index])
        oneDiff = [heur/rand for (rand, heur) in zip(randomList, heuristicList)]
        #plt.hist(oneDiff, bins = 100, alpha = 0.5, label = f"diff heur {heuristiek}")
        plt.boxplot(oneDiff, positions = [heuristiek], widths=.8)
        #plt.hist(heuristicList, bins=100, alpha=0.5, label=f"heur {heuristiek}")
    #plt.plot(randomList, label='random')
    #plt.plot(heuristicList, label='heuristic')
    plt.xlabel('heuristiek')
    plt.ylabel('tijd relatief tot willekeurige volgorde')
    plt.title("Relatieve compilatietijd bij heuristieken")
    plt.savefig("heuristieken results boxplot.png")
def __main__():
    heuristicVsRandomPlot() 
    #randomOrderPlot()
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