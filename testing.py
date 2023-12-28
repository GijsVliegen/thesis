#dot -Tpng -O sdd.dot
from randomCNFGenerator import generateRandomCnfDimacs
from randomOrderApplier import RandomOrderApply, SddVarAppearancesList
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from flatSDDCompiler import SDDcompiler
import ctypes
import os

nrOfSdds=10
nrOfVars=20
nrOfClauses=10

def testSddVarAppearances():
    #werking van varpriority testen
    nrOfSdds = 10
    nrOfVars = 16
    nrOfClauses = 10
    randApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, operation="OR", vtree_type="random")
    sddVarAppearancesList = SddVarAppearancesList(randApplier.compiler.sddManager)
    varOrdering = sddVarAppearancesList.var_order
    print(varOrdering)

    finalSdd = randApplier.doHeuristicApply(4)

def getSizes(sddManager, vars, baseSdd, operation = 0):
    newSddSizes = []
    for var in vars:
        newSdd = sddManager.apply(baseSdd, var, operation) #0 voor conjoin, 1 voor disjoin
        newSddSizes.append(newSdd.size()) #nakijken of sdds wel overeenkomen: gebruik Sdd.global_model_count()
    return newSddSizes

def testApplyOrderedVsReversed():
    """een sdd eerst opslaan,
    dan volgende zaken proberen, met balanced vtree alfabetisch order van vars: 
        applyen met eerste var, en applyen met andere var, kijken hoeveel nodes in finale resultaat
    dan, sdd omzetten naar andere vtree, kijken weet applyen met eerste var, dan met andere var, kijken hoeveel nodes in finaal resultaat."""

    """order van vars veranderen -> gebruik SddManager.var_order, reverse en Vtree.new_with_var_order"""

    """vars accessen dmv integers"""
    
    """is_var_used ook zeer interessat"""
    nrOfSdds = 1
    nrOfVars = 8
    nrOfClauses = 10 #als dit te hoog is -> kans op division door zero 
    operation = 1 #0 voor conjoin, 1 voor disjoin
    filenameStr = "testApplyOnOneVarSdd"
    byte_string = filenameStr.encode('utf-8')
    char_pointer = ctypes.create_string_buffer(byte_string)
    filenamePtr = ctypes.cast(char_pointer, ctypes.c_char_p).value
    nrOfIterations = 1000

    randomApplier = RandomOrderApply(nrOfIterations, nrOfVars, nrOfClauses, cnf3=True, operation="OR")
    orderedCompiler = SDDcompiler(nrOfVars=nrOfVars, vtree_type="left")
    varOrder = orderedCompiler.sddManager.var_order()
    startReversing = 0
    endReversing = nrOfVars#int(nrOfVars/2)
    varOrder = varOrder[:startReversing] + varOrder[startReversing:endReversing][::-1] + varOrder[endReversing:]
    reversedCompiler = SDDcompiler(nrOfVars=nrOfVars)
    reversedCompiler.sddManager = SddManager.from_vtree(Vtree.new_with_var_order(nrOfVars, varOrder, "left"))
    
    orderedVars = []
    for i in range(nrOfVars):
        orderedVars.append(orderedCompiler.sddManager.literal(i+1))
    reversedVars = []
    for i in range(nrOfVars):
        reversedVars.append(reversedCompiler.sddManager.literal(i+1))

    sizeComparisons = [0]*nrOfVars
    for i in range(nrOfIterations):
        baseSdd = randomApplier.baseSdds[i]
        baseSdd.save(filenamePtr)
        orderedSdd = orderedCompiler.sddManager.read_sdd_file(filenamePtr)
        orderedSizes = getSizes(orderedCompiler.sddManager, orderedVars, orderedSdd, operation)
        #print(f"ordered sizes : {orderedSizes}")
        reversedSdd = reversedCompiler.sddManager.read_sdd_file(filenamePtr)
        reversedSizes = getSizes(reversedCompiler.sddManager, reversedVars, reversedSdd, operation)
        #print(f"reversed sized: {reversedSizes}")
        for i in range(nrOfVars):
            if orderedSizes[i]/orderedSdd.size() > reversedSizes[i]/reversedSdd.size():
                sizeComparisons[i] += 1
    print(sizeComparisons)

    """wat kunnen we afleiden uit de resultaten: 
    AND:
    als een variabele links in de sdd staat, gaat die de sdd in het algemeen minder groter maken, dan wanneer de variabele rechts staat.
    hoe groter het aantal clauses per sdd -> hoe groter het effect
    
    waarom is het effect zo klein bij laag aantal clauses:
        size wordt vergeleken tussen sdds met 2 verschillende vtree's
        -> klein aantal clauses, vtree heeft groter effect op size van sdd
        -> vergelijking tussen sdds hangt minder af van die ene variabele en meer van die random vtree of die goed uitkomt voor die sdd
    OR:
    als een variabele links in de sdd staat, gaat die de sdd in het algemeen minder groter maken, dan wanneer de variabele rechts staat.
    hoe groter het aantal clauses per sdd -> hoe groter het effect, 
        maar ook, het effect wordt minder recursief (bv. links-rechts vs links-links weinig verschil bij groot aantal clauses)

    balanced: ...
    right-linear: het verschil tussen links en rechts is meer gradueel, maar verschil tussen uitersten is ongeveer gelijk
    left-linear: het effect van de vtree is veel groter
        -> misschien een idee om variabelen die niet zo diep in de vtree zitten als leaf, te prioriteren"""
    
    """aantal clauses ~ complexiteit van sdd
    complexiteit van sdd ~ ?"""
def testApplyOnOneVar():
    nrOfVars = 16
    nrOfClauses = 40     
    operation = 0 #0 voor conjoin, 1 voor disjoin
    nrOfIterations = 100

    randomApplier = RandomOrderApply(nrOfIterations, nrOfVars, nrOfClauses, cnf3=True, operation="OR")
    vars = []
    for i in range(nrOfVars):
        vars.append(randomApplier.compiler.sddManager.literal(i+1))

    sizeComparisons = [0]*nrOfVars
    for i in range(nrOfIterations):
        baseSdd = randomApplier.baseSdds[i]
        sizes = getSizes(randomApplier.compiler.sddManager, vars, baseSdd, operation)
        #print(f"ordered sizes : {orderedSizes}")
        for i in range(nrOfVars):
            sizeComparisons[i] += sizes[i]/baseSdd.size() #lager getal geeft aan dat sdd algemeen kleiner wordt

    for i in range(nrOfVars):
        sizeComparisons[i] /= nrOfIterations
        sizeComparisons[i] = round(sizeComparisons[i], 3)
    print(sizeComparisons)
    """uit de resultaten van deze test kunnen we ook zien dat als geapplied wordt op een var aan de linkerkant, 
    dit in het algemeen de sdd kleiner zal maken dan wanneer de var rechts zit"""


def testDimacs():
    print(generateRandomCnfDimacs(nrOfClauses, nrOfVars))

def testMinimization():
    randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, cnf3=True, operation="OR")
    baseSdd0 = randomApplier.baseSdds[0]
    print(f"grootte: base sdd heeft size {baseSdd0.count()} en {randomApplier.compiler.sddManager.count()} nodes in de sddManager")

    output_directory = "/home/gijs/school/23-24/thesisUbuntu/output"
    file_path_vtree0 = os.path.join(output_directory, "vtree0.dot")
    with open(file_path_vtree0, "w") as out:
        print(randomApplier.compiler.sddManager.vtree().dot(), file=out)

    randomApplier.minimize_base_sdds()
    print(f"grootte: base sdd heeft size {baseSdd0.count()} en {randomApplier.compiler.sddManager.count()} nodes in de sddManager")

    file_path_vtree1 = os.path.join(output_directory, "vtree1.dot")
    with open(file_path_vtree1, "w") as out:
        print(randomApplier.compiler.sddManager.vtree().dot(), file=out)


    sdd = randomApplier.doRandomApply()
    print(f"grootte: sdd heeft size {sdd.count()} en {randomApplier.compiler.sddManager.count()} nodes in de sddManager")

    randomApplier.minimize_with_all()
    print(f"grootte: sdd heeft size {sdd.count()} en {randomApplier.compiler.sddManager.count()} nodes in de sddManager")
    file_path_vtree2 = os.path.join(output_directory, "vtree2.dot")
    with open(file_path_vtree2, "w") as out:
        print(randomApplier.compiler.sddManager.vtree().dot(), file=out)

    randomApplier.minimize_only_final()
    print(f"grootte: sdd heeft size {sdd.count()} en {randomApplier.compiler.sddManager.count()} nodes in de sddManager")
    file_path_vtree3 = os.path.join(output_directory, "vtree3.dot")
    with open(file_path_vtree3, "w") as out:
        print(randomApplier.compiler.sddManager.vtree().dot(), file=out)

def testVtreeFunctions():
    randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, cnf3=True, operation="OR")
    oneSdd = randomApplier.baseSdds[0]
    print(oneSdd.vtree())
    if (Vtree.is_sub(oneSdd.vtree(), oneSdd.vtree().left())):
        print("yeet")
    rootNode = oneSdd.vtree()
    print(f"id = {rootNode.position()}")
    leftNode = rootNode.left()
    rightNode = rootNode.right()
    print(f"left id = {leftNode.position()}")
    print(f"right id = {rightNode.position()}")

heuristicsList = [1, 2, 3, 4]
def testCorrectWorkingHeuristics():
    workingCorrect = True
    randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, cnf3=True, operation="OR")
    finalSdd = randomApplier.doRandomApply()
    for heuristic in heuristicsList:
        if finalSdd != randomApplier.doHeuristicApply(heuristic):
            print(f"er is iets mis met heuristic {heuristic}")
            workingCorrect = False
    if workingCorrect:
        print("heuristieken werken correct")

def getVtreeFig():
    randomApplier = RandomOrderApply(20, 15, 10, 1, cnf3=True, operation="OR")
    finalSdd = randomApplier.doRandomApply()
    with open("vtree.dot", "w") as out:
        print(finalSdd.vtree().dot(), file = out)


testCorrectWorkingHeuristics()
#testVtreeFunctions()
#getVtreeFig()
#testApplyOrderedVsReversed()
#testApplyOnOneVar()
#testSddVarAppearances()

"""

output_directory = "/home/gijs/school/23-24/thesisUbuntu/output"
file_path_sdd = os.path.join(output_directory, "smallerSdd.dot")
file_path_vtree0 = os.path.join(output_directory, "smallerVtree.dot")
file_path_vtree1 = os.path.join(output_directory, "firstVtree.dot")
file_path_vtree2 = os.path.join(output_directory, "smallerVtree2.dot")

#Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

with open(file_path_vtree0, "w") as out:
    print(sdd.vtree().dot(), file = out)

# randomApplier.compiler.sddManager.minimize() //werkt niet -> sdd access verwijderd
# print(f"grootte: sdd heeft size {sdd.count()} en {sdd.count()} nodes")
smallerSdd = randomApplier.compiler.sddManager.minimize_cardinality(sdd)
print(f"grootte: kleinere sdd heeft size {smallerSdd.count()} en {smallerSdd.count()} nodes")

# Visualize SDD and Vtree
with open(file_path_sdd, "w") as out:
    print(smallerSdd.dot(), file=out)
with open(file_path_vtree1, "w") as out:
    print(smallerSdd.vtree().dot(), file=out)

smallerVtree2 = randomApplier.compiler.sddManager.vtree_minimize(sdd.vtree())
with open(file_path_vtree2, "w") as out:
    print(smallerVtree2.dot(), file=out)

"""

print("einde programma")
