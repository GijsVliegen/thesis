import pickle, pprint
from thesis_files.propositional_formula import FormulaContainer, FormulaOp, RefFormula
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from functools import reduce
from dataclasses import dataclass
import matplotlib.pyplot as plt
import os
import timeit
import random

def load_formula_from_pickle(filename: str) -> FormulaContainer:
    with open(filename, "rb") as f:
        formula = pickle.load(f)
    return formula

"""slaat literals op dmv een dict, kan gereferenced worden mbv de nodeId, dit is nodig omdat meerdere Nodes
naar bep literals kunnen verwijzen"""
literalSdds = {} #dict
def getLiteralSdd(nodeId, sddManager):
    if nodeId in literalSdds:
        return literalSdds[nodeId]
    else:
        newId = len(literalSdds) + 1
        literalSdds[nodeId] = sddManager.literal(newId)
        return literalSdds[nodeId]

"""wordt niet meer gebruikt"""
def getChildNode(rootNode, formula, childNr) -> RefFormula:
    childId = rootNode.children[childNr]
    return formula.get_formula(childId)

def insort_right(sortedList, newElement, key, lo=0, hi=None):
    """Insert item x in list a, and keep it sorted assuming a is sorted.
    If x is already in a, insert it to the right of the rightmost x.
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    newElementVal = key(newElement)
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(sortedList)
    while lo < hi:
        mid = (lo + hi) // 2
        if newElementVal < key(sortedList[mid]):
            hi = mid
        else:
            lo = mid + 1
    sortedList.insert(lo, newElement)

    



"""bevat de heuristiek implementatie

kiest de volgende twee sdd's uit een lijst, die daarna geapplied moeten worden
ook tussenresultaten worden hier geregistreerd

goeie vraag of een heuristiek eventueel operationInt kan/moet gebruiken voor zijn werking

voor heuristieken de zich baseren op de ene sdd zelf, gebruik sorted list en maintain die, element toevoegen = O(log n)
-> complexiteit O(n*log(n)), met n = aantal kinderen

voor heuristieken die de combinatie van twee sdd's gebruikt, is een cache object nodig (lijst of dict ofzo), die de heuristiekwaarde voor dat paar bijhoudt
-> met cache, O(n^2); zonder cache, O(n^3), met n = aantal kinderen

mogelijke heuristieken zijn:
0 -> default
99 -> random volgorde
--------lineare heuristieken--------------
1 -> grootte van sdd
    DataStructure = sorted list
        -> O(1) om te deleten vooraan
        -> O(log(n)) om te inserten
    of DataStructure = sorted list
        -> O(n) om te deleten vooraan, maar puur op het aantal keer adressen
        -> O(log(n)) om te inserten

--------kwadratische heuristieken------------
10 -> verwachte grootte / upper bound van de apply op 2 sdd's
11 -> verwacht aantal vars / upper bound van de apply op 2 sdd's
"""
HEURISTIEK = 0 #default #HIER NIET HEURISTIEK AANPASSEN, DOE VANONDER

def getNextSddToApply(childrenSdd, dataStructure = None):
    if HEURISTIEK == 0: 
        return childrenSdd[-1], childrenSdd[-2], None
    elif HEURISTIEK == 1:
        if dataStructure is None:
            #dataStructure = deque(sorted(childrenSdd, key=lambda sdd: sdd.size()))  #eventuele deque implementatie
            dataStructure = sorted(childrenSdd, key=lambda sdd: sdd.size())
            return dataStructure.pop(0), dataStructure.pop(0), dataStructure
        else:
            return dataStructure.pop(0), dataStructure.pop(0), dataStructure
    elif HEURISTIEK == 99:
        firstInt = random.randint(0, len(childrenSdd)-1)
        firstSdd = childrenSdd[firstInt]
        secondInt = firstInt
        while (secondInt == firstInt):
            secondInt = random.randint(0, len(childrenSdd)-1)
        secondSdd = childrenSdd[secondInt]
        return firstSdd, secondSdd, None
    else: 
        print("er is iets mis, heuristiek heeft geen correcte waarde / implementatie")
        return None, None, None

"""deel 2 van de heuristiek, dient voor het onderhouden van de datastructure/list"""
def updateDatastructure(newSdd, childrenSdd, datastructure):
    if HEURISTIEK == 0: 
        pass
    elif HEURISTIEK == 1: 
        insort_right(datastructure, newSdd, key=lambda sdd: sdd.size())
    elif HEURISTIEK == 99:
        pass
    else: 
        print("er is iets mis, heuristiek heeft geen correcte waarde / implementatie")

@dataclass
class oneResult:
    rootNodeId: int
    nrOfChildren: int
    tussenresultaatSizes: [int]

"""slaat de nodige resultaten op afhankelijk van de heuristiek

manier van opslaan: nodeId + aantal kinderen + grootte van alle tussenresultaten in volgorde van applied"""
resultsDict = {}
def doSomethingWithResults(parentId, parentNode, newSdd, dataStructure):
    if parentId not in resultsDict:
        resultsDict[parentId] = oneResult(parentId, len(parentNode.children), [newSdd.size()])
    else:
        resultsDict[parentId].tussenresultaatSizes.append(newSdd.size())

def saveResults(filename, rootNodeId):
    os.makedirs(f"results/{filename}",exist_ok=True)
    with open(f"results/{filename}/result_{rootNodeId}_{HEURISTIEK}.txt", 'w') as file:
        # Iterate through the dictionary items and write them to the file
        for key, value in resultsDict.items():
            file.write(f'Node {key}: {value}\n')


"""compiled vanaf een rootnode de formule naar een sdd, werkt recursief

best in deze functie de heuristiek inbouwen dmv apply_total functie te veranderen/vervangen"""
def compileToSdd(rootNode : RefFormula, formula, sddManager, rootNodeId):

    #print(f"children of this node are {rootNode.children}")
    if(rootNode.op == FormulaOp.ATOM):
        return (getLiteralSdd(rootNodeId, sddManager), 1)
    
    if(rootNode.op == FormulaOp.NEG): #neg telt niet mee tot het aantal elementen in de DAG imo
        childNode = formula.get_formula(rootNode.children[0])
        (sdd, totalNodesInDag) = compileToSdd(childNode, formula, sddManager, rootNode.children[0])
        return (sddManager.negate(sdd), totalNodesInDag)

    #sdd = compileToSdd(getChild(formula, rootNode, 0), formula, sddManager)
    childNodes = map(formula.get_formula, rootNode.children)
    childrenSdd, sizeOfChildrenDag = map(list, zip(*map(lambda childNode, childId: compileToSdd(childNode, formula, sddManager, childId), childNodes, rootNode.children)))
    
    #is de operatie conjoin (0) of disjoin (1)
    operationInt = 0 if rootNode.op == FormulaOp.CONJ else 1
    
    datastructure = None
    while len(childrenSdd) > 1:
        sdd1, sdd2, datastructure = getNextSddToApply(childrenSdd, datastructure)
        childrenSdd.remove(sdd1)
        childrenSdd.remove(sdd2)
        newSdd = sddManager.apply(sdd1, sdd2, operationInt)
        updateDatastructure(newSdd, childrenSdd, datastructure) #eerst dataStructure updaten, die gebruikt maakt van alle 
        #overige elementen in childrenSdd, pas daaarne newSdd toevoegen aan childrenSdd
        childrenSdd.append(newSdd)
        doSomethingWithResults(rootNodeId, rootNode, newSdd, datastructure)
    """
    voor de standaard apply zonder heuristiek:
    
    apply_total = lambda ssd1, sdd2: sddManager.apply(ssd1, sdd2, operationInt)
    combinedSdd = reduce(apply_total, childrenSdd)"""
    
    return (childrenSdd[0], sum(sizeOfChildrenDag) + 1)

"""
constante die de heuristiek bepaalt.
kan zijn:
0 -> default
--------lineare heuristieken--------------
1 -> grootte van sdd
2 -> aantal vars
--------kwadratische heuristieken------------
10 -> verwachte grootte / upper bound van de apply op 2 sdd's
11 -> verwacht aantal vars / upper bound van de apply op 2 sdd's
"""  

def main(filename: str, rootNodeId : int, firstTime = False):

    formula = load_formula_from_pickle(f"{filename}.pickle")
    nrOfVars = formula.get_nb_vars()
    
    vtree = Vtree(var_count=nrOfVars, vtree_type="balanced") #kan nog aangepast worden voor experiment
    sddManager = SddManager.from_vtree(vtree)
    
    if firstTime:
        #stukje code om nodes met veel kinderen te vinden, voor lijst zie vanonder
        lastDagSize = 0
        for index, node in enumerate(formula):
            literalSdds = {}
            if len(node.children) > 4:
                (sdd, nodesInDAG) = compileToSdd(node, formula, sddManager, len(formula)) #laatste node is de root node
                if nodesInDAG == lastDagSize:
                    formulaInformation = "idem"
                else:
                    formulaInformation = f"totale grootte = {sdd.size()}, aantal nodes in OG DAG = {nodesInDAG}, aantal vars = {len(literalSdds)}"
                print(f"node {index} bevat {len(node.children)} kinderen -> {formulaInformation}")
                lastDagSize = nodesInDAG
    else:
        rootNode = formula.get_formula(rootNodeId)
        (sdd, nodesInDAG) = compileToSdd(rootNode, formula, sddManager, len(formula)) #laatste node is de root node
        #print(f"totale grootte = {sdd.size()}, aantal nodes in OG DAG = {nodesInDAG}, aantal vars = {len(literalSdds)}")
        saveResults(filename, rootNodeId)

def mainCompile(formula, rootNodeId):

    nrOfVars = formula.get_nb_vars()
    vtree = Vtree(var_count=nrOfVars, vtree_type="balanced") #kan nog aangepast worden voor experiment
    sddManager = SddManager.from_vtree(vtree)
    rootNode = formula.get_formula(rootNodeId)
    compileToSdd(rootNode, formula, sddManager, len(formula)) #laatste node is de root node
    #print(f"totale grootte = {sdd.size()}, aantal nodes in OG DAG = {nodesInDAG}, aantal vars = {len(literalSdds)}")
    #sddManager.minimize()

HEURISTIEK = 99 #HIER HEURISTIEK AANPASSEN!!!!
rootNodeId = 208
filename = "thesis_files/alarm_sAO2_normal"
main(filename, rootNodeId, firstTime=True)
"""
nrOfIterations = 2
results = []
formula = load_formula_from_pickle(f"{filename}.pickle")
for j in range(nrOfIterations):
    print(j)
    timer = timeit.Timer(stmt=lambda: mainCompile(formula, rootNodeId))
    execution_time = timer.timeit(number=1)
    results.append(execution_time)


# Plot the range of integers for each key
plt.plot(range(nrOfIterations), results, 'o') 

# Add labels and a legend
plt.yscale("log")
plt.xlabel('try')
plt.ylabel('total comp time')

# Show the plot
plt.show()
plt.savefig(f"results/randomOrderCompTimeVariationPickle.png")"""

"""
----------alarm_sAO2_normal------------------
node 64 bevat 8 kinderen -> totale grootte = 1044, aantal nodes in OG DAG = 113, aantal vars = 24
node 93 bevat 8 kinderen -> idem
node 114 bevat 8 kinderen -> idem
node 135 bevat 8 kinderen -> idem
node 208 bevat 24 kinderen -> totale grootte = 9742, aantal nodes in OG DAG = 2857, aantal vars = 76
node 284 bevat 24 kinderen -> idem
node 336 bevat 24 kinderen -> idem
node 388 bevat 24 kinderen -> idem
node 416 bevat 12 kinderen -> totale grootte = 107191, aantal nodes in OG DAG = 34333, aantal vars = 160
node 456 bevat 12 kinderen -> idem
node 484 bevat 12 kinderen -> idem
node 512 bevat 12 kinderen -> idem
node 530 bevat 8 kinderen -> totale grootte = 142072, aantal nodes in OG DAG = 274697, aantal vars = 206
node 551 bevat 6 kinderen -> totale grootte = 57, aantal nodes in OG DAG = 31, aantal vars = 213
node 573 bevat 6 kinderen -> idem
node 601 bevat 8 kinderen -> totale grootte = 142758, aantal nodes in OG DAG = 274697, aantal vars = 227
node 624 bevat 8 kinderen -> idem
node 631 bevat 6 kinderen -> totale grootte = 622691, aantal nodes in OG DAG = 1648387, aantal vars = 241

----------alarm_pRESS_zero-------------------
node 63 bevat 8 kinderen -> totale grootte = 25, aantal nodes in OG DAG = 14, aantal vars = 8
node 92 bevat 8 kinderen -> idem
node 113 bevat 8 kinderen -> idem
node 134 bevat 8 kinderen -> idem
node 207 bevat 24 kinderen -> totale grootte = 1075, aantal nodes in OG DAG = 119, aantal vars = 27

----------alarm_bP_low-----------------------
node 63 bevat 8 kinderen -> totale grootte = 33, aantal nodes in OG DAG = 14, aantal vars = 8
node 92 bevat 8 kinderen -> idem
node 113 bevat 8 kinderen -> idem
node 134 bevat 8 kinderen -> idem
node 207 bevat 24 kinderen -> totale grootte = 932, aantal nodes in OG DAG = 119, aantal vars = 27
node 283 bevat 24 kinderen -> idem
node 335 bevat 24 kinderen -> idem
node 387 bevat 24 kinderen -> idem
node 415 bevat 12 kinderen -> totale grootte : 25326, aantal nodes in OG DAG = 2861, aantal vars = 77
node 454 bevat 12 kinderen -> idem
node 481 bevat 12 kinderen -> idem
node 508 bevat 12 kinderen -> idem
node 540 bevat 8 kinderen -> totale grootte = 128743, aantal nodes in OG DAG = 34337, aantal vars = 162
node 611 bevat 8 kinderen
node 634 bevat 8 kinderen
node 905 bevat 54 kinderen
node 1070 bevat 54 kinderen
node 1152 bevat 9 kinderen
node 1189 bevat 9 kinderen
node 1217 bevat 9 kinderen
node 1227 bevat 9 kinderen"""