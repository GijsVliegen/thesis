import argparse
import matplotlib.pyplot as plt
import pyperf
import pylab
import scipy.stats as stats

def randomOrderPlot():
    filename = "output/randomOrderCompTimeVariation_20_10_OR_reverse.txt"
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

        nrOfClausesList.append(int(line[:start_pos].split(" ")[1]))
        current_list = sorted(current_list)[5:-5] #5 grootste en kleinste elementen weglaten om eventuele foute uitschieters weg te laten
        lists.append(current_list)
    plotMaxMinAverageList(lists)

def plotMaxMinAverageList(lists):
    averageList = []
    maxList = []
    minList = []
    for list in lists:        
        max = 0
        min = 99999
        sum = 0
        for i in list:
            if i > max:
                max = i
            if i < min:
                min = i
            sum += i
        averageList.append(sum/len(list))
        maxList.append(max)
        minList.append(min)

    plt.plot(minList, label='min')
    plt.plot(averageList, label='average')
    plt.plot(maxList, label='max')

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
    filename = "output/randomVsHeuristic_20_10_10_OR_1.txt"
    with open(filename, 'r') as file:
        # Read lines from the file
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    
    randomList = getListFromLine(lines[1])
    heuristicList = getListFromLine(lines[2])

    plt.hist(randomList, bins=100, alpha=0.5, label='random')
    plt.hist(heuristicList, bins=100, alpha=0.5, label='heuristic')

def __main__():
    heuristicVsRandomPlot() 
    plt.xlabel('X-axis Label')
    plt.ylabel('Y-axis Label')
    plt.yscale('log')
    plt.legend()
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