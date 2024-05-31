#dot -Tpng -O sdd.dot
from randomCNFGenerator import generateRandomCnfDimacs
from heuristicApplier import HeuristicApply, SddVarAppearancesList, SddVtreeCountList
from heuristicApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, \
    EL, ELVAR, VP_ELVAR, IVO_RL_EL
from heuristicApplier import AND, OR

from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from flatSDDCompiler import SDDcompiler
import ctypes
import os
import timeit
import graphviz
import itertools
import math

nrOfSdds=10
nrOfVars=20
nrOfClauses=10

def varOrderTest():
    nrOfSdds=2
    nrOfVars=15
    nrOfClauses = 5#25#[5, 15, 25, 35, 45, 55, 65]
    #nrOfIterations = 10
    operation = OR
    randomApplier = HeuristicApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type="random")
    vtree = randomApplier.compiler.sddManager.vtree() 
    sdds = randomApplier.baseSdds
    varAppList = SddVarAppearancesList(sdds, randomApplier.compiler.sddManager)
    varAppOrder = varAppList.var_order
    ReverseLRvarAppList = SddVarAppearancesList(sdds, randomApplier.compiler.sddManager, inverse=True, LR = True)
    ReverseLRvarAppOrder = ReverseLRvarAppList.var_order
    ReverseRLvarAppList = SddVarAppearancesList(sdds, randomApplier.compiler.sddManager, inverse=True, LR = False)
    ReverseRLvarAppOrder = ReverseRLvarAppList.var_order
    print(f"var order = {varAppOrder}")
    print(f"inverse var order LR = {ReverseLRvarAppOrder}")
    print(f"inverse var order RL = {ReverseRLvarAppOrder}")
    with open(f"testing/varOrderTest_random_vtree", "w") as out:
        print(vtree.dot(), file=out)
        graphviz.Source(vtree.dot()).render(f"testing/varOrderTest_random_vtree", format='png')
    
def varsUnderVtreeNode_test():
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="balanced")
    # 3:{all}
    # 1:{a,b}      5:{c,d}
    # 0:{a} 2:{b}  4:{c}    6:{d}
    mgr = SddManager.from_vtree(vtree)
    a, b, c, d = mgr.vars
    f2 = a
    f3 = (~a & (b | c | d)) | (a & c)
    f2vars = mgr.sdd_variables(f2)[1:]
    f3vars = mgr.sdd_variables(f3)[1:]
    print(SddVtreeCountList.varsUnderVtreeNode(f2vars, vtree))
    print(SddVtreeCountList.varsUnderVtreeNode(f3vars, vtree))

    randomApplier = HeuristicApply(nrOfSdds, 15, 75, vtree_type="random")
    mgr = randomApplier.compiler.sddManager
    vtree = mgr.vtree() 
    sdds = randomApplier.baseSdds
    varCounts = [sum(mgr.sdd_variables(sdd)) for sdd in sdds]
    print(varCounts)

    

def overheadTime_test():
    heuristics = [RANDOM, KE, VP, VP_KE, VO, EL]
    nrOfSdds=20
    nrOfVars=15
    nrOfClauses = 5#25#[5, 15, 25, 35, 45, 55, 65]
    #nrOfIterations = 10
    operation = OR
    randomApplier = HeuristicApply(nrOfSdds, nrOfVars, nrOfClauses, vtree_type="random")
    for heuristic in heuristics:
        (resultSdd, noOverheadTime) = randomApplier.doHeuristicApply(heuristic, operation, timeOverhead=False)
        totalTime = timeit.timeit(lambda: randomApplier.doHeuristicApply(heuristic, operation), number = 1)
        print(f"heur {heuristic}: total time = {totalTime}, zonder overhead = {noOverheadTime}")
    
def optimal_heuristic_test():
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="balanced")
    # 3:{all}
    # 1:{a,b}      5:{c,d}
    # 0:{a} 2:{b}  4:{c}    6:{d}
    mgr = SddManager.from_vtree(vtree)
    a, b, c, d = mgr.vars
    f1 = (~a & (b | c | d))
    f2 = a
    f3 = (~a & (b | c | d)) | (a & c)
    f12 = f1 & f2 #= \bot
    f23 = f2 & f3 #= (a & c)
    f123 = f12 & f3 #= \bot
    for (index, sdd) in enumerate([f1, f2, f3, f12, f23, f123]):
        with open(f"sdd{index}", "w") as out:
            print(sdd.dot(), file=out)
            graphviz.Source(sdd.dot()).render(f"sdd{index}", format='png')


def vtree_count_implementation_test():
    """test together with debugging to see if _getUpperLimit() works correctly"""
    """ test node.vtree_element_count() on an SDDNode with more than 2 elements """
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="balanced")
    # 3:{all}
    # 1:{a,b}      5:{c,d}
    # 0:{a} 2:{b}  4:{c}    6:{d}
    mgr = SddManager.from_vtree(vtree)
    a, b, c, d = mgr.vars
    # a & b -> c
    # a & -b -> c&d
    # b -> -c
    f1 = ~(a & b) #onder 1
    f2 = ~(a & ~b) | (c & d) #onder 3
    f3 = ~c #onder 4
    f4 = d #onder 6
    f5 = f3 & f4 | c #onder 5
    # Source(f4.dot()).view()
    sdds = [f1, f2, f3, f4, f5]
    for i in range(len(sdds)):
        for j in range(i+1, len(sdds)):
            print(f"f{i+1} met f{j+1}: {(sdds[i] & sdds[j]).local_vtree_element_count()}")
    for sdd in sdds:
        print(sdd.local_vtree_element_count())
    sddVtreeCountList = SddVtreeCountList(sdds, mgr)
    print(sddVtreeCountList.getNextSddsToApply()) 
    # print(SddVtreeCountList._getVtreeOrder(f5.vtree())) --functie is wss niet meer nodig, maar bevat ook een segmentatiefout


def local_vtree_count_tests():
    """ test node.vtree_element_count() on a small SDD, with vtree type left """
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="left")
    #                       5:{all}
    #               3:{a,b,c}   6:{d}
    #       1:{a,b}     4:{c}
    #  0:{a}    2:{b}
    mgr = SddManager.from_vtree(vtree)
    a, b, c, d = mgr.vars
    # verify vtree element count for decision
    f1 = ~(a & b) #onder 1
    f2 = ~(a & ~b) | (c & d) #onder 3
    f3 = ~c #onder 4
    f4 = f1 & f3
    with open(f"primesWithSubs", "w") as out:
        print(f4.dot(), file=out)
    graphviz.Source(f4.dot()).render(f"primesWithSubs", format='png')
    print(f1.local_vtree_element_count())
    # vtreeOrderList = SddVtreeCountList(f3)

def generate_all_sdd_test():
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="left")
    #                       5: {a, b, c, d}
    #               3: {a, b, c}        6: {d}
    #       1:{a,b}         4:{c}
    #  0:{a}    2:{b}
    sddmgr = SddManager.from_vtree(vtree)
    a = SddManager.literal(sddmgr, 1)
    NOTa = SddManager.literal(sddmgr, -1)
    b = SddManager.literal(sddmgr, 2)
    NOTb = SddManager.literal(sddmgr, -2)
    c = SddManager.literal(sddmgr, 3)
    NOTc = SddManager.literal(sddmgr, -3)
    d = SddManager.literal(sddmgr, 4)
    NOTd = SddManager.literal(sddmgr, -4)
    baseSdds = [a, NOTa, b, NOTb, c, NOTc]#, d, NOTd]#, trueSdd, falseSdd] #met d erbij duurt veel te lang: meer dan 50000 sdds mogelijk

    # exists = (a.conjoin(b)).disjoin(NOTa.conjoin(NOTb))
    # with open(f"allSdds/exists", "w") as out:
    #     print(exists.dot(), file=out)
    # graphviz.Source(exists.dot()).render(f"allSdds/exists", format='png')
    
    #bevat alle mogelijke sdds
    powersetSdd = set(baseSdds)
    for index in range(len(baseSdds)):
        print(index)
        for sdd in powersetSdd.copy():
            for i in powersetSdd.copy():
                powersetSdd.add(i.conjoin(sdd))
                powersetSdd.add(i.disjoin(sdd))
            powersetSdd.add(sdd)
    
    # kijken hoeveel sdds hoeveel elementen hebben onder vtree knoop v
    # dmv. stukje code om aantal partities te tellen: partities van x elementen kunnen (y! / (y-x)! /x!)? subs bevatten
    primesets = []
    subsset = []
    rootVtreeNodeIndex = 3
    varsInRootPrimes = 2
    for (index, nrOfElements) in enumerate(range(2, 2**varsInRootPrimes+1)):
        print(index)
        primesets.append(set())
        subsset.append(set())
        sum = 0
        for i in powersetSdd:
            if i.local_vtree_element_count()[rootVtreeNodeIndex] == nrOfElements:
                sum += 1
                setOfPrimes = frozenset([x[0] for x in i.elements()])
                primesets[index].add(setOfPrimes)
                setOfSubs = frozenset([x[1] for x in i.elements()])
                subsset[index].add(setOfSubs)

    for i in range(len(primesets)):
        print(f"voor {i+2}:")
        print(f"primes = {len(primesets[i])}" )
        print(f"subs = {len(subsset[i])}" )
    #print(f"aantal sdds met {nrOfElements} voor root vtree knoop = {sum}")
    print("yeet")
    
    # setOfPrimeSets = set()
    # for i in powersetSdd:
    #     if i.local_vtree_element_count()[3] != 0:
    #         setOfPrimes = frozenset([x[0] for x in i.elements()])
    #         # if setOfPrimes not in setOfPrimeSets:
    #             # for (index, sdd) in enumerate(setOfPrimes):
    #             #     with open(f"allSdds/primeSet{index}", "w") as out:
    #             #         print(sdd.dot(), file=out)
    #             #     graphviz.Source(sdd.dot()).render(f"allSdds/primeSet{index}", format='png')
    #             # print("breakpoint")
    #         setOfPrimeSets.add(setOfPrimes)
    # for i in setOfPrimeSets:
    #     print(len(i))
    # for (index, sdd) in enumerate(powersetSdd):
    #     with open(f"allSdds/{index}", "w") as out:
    #         print(sdd.dot(), file=out)
    #     graphviz.Source(sdd.dot()).render(f"allSdds/{index}", format='png')
    print("done")

def negation_test(): 
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="balanced")
    #                       5:{all}
    #               3:{a,b,c}   6:{d}
    #       1:{a,b}     4:{c}
    #  0:{a}    2:{b}
    mgr = SddManager.from_vtree(vtree)
    a, b, c, d = mgr.vars
    f1 = a & b
    f2 = b & (c|d)
    f5 = f1 | f2
    f6 = ~f5
    with open("sdd5", "w") as out:
        print(f5.dot(), file=out)
    graphviz.Source(f5.dot()).render(f"sdd5", format='png')
    with open("sdd6", "w") as out:
        print(f6.dot(), file=out)
    graphviz.Source(f6.dot()).render(f"sdd6", format='png')

def sdd_graphical_research_test():
    nrOfSdds=20
    nrOfVars=16
    operation="OR"
    listNrOfClauses=list(tuple(range(2, int(nrOfVars*5), 4)))

    for (i, nrOfClauses) in enumerate(listNrOfClauses):
        fileName = "f"+str(i)
        randomApplier = HeuristicApply(nrOfSdds, nrOfVars, nrOfClauses, nrOfCnfs=1, cnf3=True, operation = operation)
        sdd = randomApplier.baseSdds[0]
        print(sdd.local_vtree_element_count())
        # with open(f"vtree_count_implementation_test_sdds/{fileName}.dot", "w") as out:
        #     print(sdd.dot(), file = out)
        # graphviz.Source(sdd.dot()).render("vtree_count_implementation_test_sdds/"+fileName, format='png')

def countingTests():
    nrOfSdds = 10
    nrOfVars = 16
    nrOfClauses = 10
    randApplier = HeuristicApply(nrOfSdds, nrOfVars, nrOfClauses, operation="OR", vtree_type="random")
    finalSdd = randApplier.doHeuristicApply(4)
    counts = randApplier.extractCounts()
    for i in counts:
        (c, lc, dc) = i
        print(f"live count = {lc}, dead count = {dc}, total count = {c}")

def testSddVarAppearances():
    #werking van varpriority testen
    vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="balanced")
    #                       5:{all}
    #               3:{a,b,c}   6:{d}
    #       1:{a,b}     4:{c}
    #  0:{a}    2:{b}
    mgr = SddManager.from_vtree(vtree)
    a, b, c, d = mgr.vars
    f1 = b      #[0, 1, 0, 0]
    f2 = a      #[1, 0, 0, 0]
    f3 = a | b  #[1, 1, 0, 0]
    f4 = a | d  #[1, 0, 0, 1]
    sddVarAppList = SddVarAppearancesList([f1, f2, f3, f4], mgr)
    assert sddVarAppList.pop(0) == f2
    assert sddVarAppList.pop(0) == f3
    assert sddVarAppList.pop(0) == f4
    assert sddVarAppList.pop(0) == f1

    # nrOfSdds = 10
    # nrOfVars = 16
    # nrOfClauses = 10
    # randApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, operation="OR", vtree_type="random")
    # sddVarAppearancesList = SddVarAppearancesList(randApplier.compiler.sddManager)
    # varOrdering = sddVarAppearancesList.var_order
    # print(varOrdering)
    # finalSdd = randApplier.doHeuristicApply(4)

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
    nrOfVars = 8
    nrOfClauses = 10 #als dit te hoog is -> kans op division door zero 
    operation = OR #0 voor conjoin, 1 voor disjoin
    filenameStr = "testApplyOnOneVarSdd"
    byte_string = filenameStr.encode('utf-8')
    char_pointer = ctypes.create_string_buffer(byte_string)
    filenamePtr = ctypes.cast(char_pointer, ctypes.c_char_p).value
    nrOfIterations = 1000

    randomApplier = HeuristicApply(nrOfIterations, nrOfVars, nrOfClauses)
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

    randomApplier = HeuristicApply(nrOfIterations, nrOfVars, nrOfClauses, cnf3=True, operation="OR")
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
    randomApplier = HeuristicApply(nrOfSdds, nrOfVars, nrOfClauses, cnf3=True, operation="OR")
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
    randomApplier = HeuristicApply(1, 16, 5, vtree_type="random")
    vtree = randomApplier.compiler.sddManager.vtree()
    with open("vtree", "w") as out:
        print(vtree.dot(), file=out)
    graphviz.Source(vtree.dot()).render(f"vtree", format='png')

def testCorrectWorkingHeuristics():
    heuristicsList = [IVO_RL_EL] #[RANDOM, KE, VP, \
                    #   VP_KE, VO, \
                    #     EL, IVO_LR, IVO_RL, ELVAR, VP_ELVAR]
    nrOfVars = 16
    nrOfClausesList = [5, 25, 40, 55, 75]
    operations = [OR, AND] #0 voor conjoin, 1 voor disjoin
    nrOfIterations = 10
    workingCorrect = True
    for nrOfClauses in nrOfClausesList:
        for operation in operations:
            print(f"aantal clauses = {nrOfClauses}, operatie = {operation}")
            randomApplier = HeuristicApply(nrOfSdds, nrOfVars, nrOfClauses, OR, 150, vtree_type="balanced")
            for _ in range(nrOfIterations):
                finalSdd = randomApplier.doHeuristicApply(RANDOM, operation)[0].getSdd()
                for heuristic in heuristicsList:
                    otherSdd = randomApplier.doHeuristicApply(heuristic, operation)[0].getSdd()
                    if finalSdd != otherSdd:
                        print(f"er is iets mis met heuristic {heuristic}")
                        workingCorrect = False
                randomApplier.renew()
    if workingCorrect:
        print("heuristieken werken correct")

def getVtreeFig():
    randomApplier = HeuristicApply(20, 15, 10, 1, cnf3=True, operation="OR")
    finalSdd = randomApplier.doRandomApply()
    with open("vtree.dot", "w") as out:
        print(finalSdd.vtree().dot(), file = out)

#varsUnderVtreeNode_test()
#overheadTime_test()
#optimal_heuristic_test()
#generate_all_sdd_test()
#sdd_graphical_research_test()
#vtree_count_implementation_test()
#local_vtree_count_tests()
#negation_test()
#countingTests()
#getVtreeFig()
#testApplyOrderedVsReversed()
#testApplyOnOneVar()
#testSddVarAppearances()
#varsUnderVtreeNode_test()
#varOrderTest()

testCorrectWorkingHeuristics() #RESULT SDD TERUGGEGEN IN RandomOrderApplier
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
