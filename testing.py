#dot -Tpng -O sdd.dot
from randomCNFGenerator import generateRandomCnfDimacs
from randomOrderApplier import RandomOrderApply
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
import os

nrOfSdds=10
nrOfVars=20
nrOfClauses=10

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

heuristicsList = [1, 2]
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


#testCorrectWorkingHeuristics()
#testVtreeFunctions()
getVtreeFig()

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
