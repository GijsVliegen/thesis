import pickle, pprint
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from randomCNFGenerator import generateRandomCnf
from flatSDDCompiler import SDDcompiler

#dot -Tpng -O sdd.dot

def saveToPickle(filename, data):

    with open(filename, 'wb') as file:
        # Use pickle.dump() to serialize and save the object to the file
        pickle.dump(data, file)

"""
n variables and m clauses, where
n = 40, 45, and 50, and m ranges from 10 to 5n at intervals of 5. For each n-m
combination we generate 20 instances.
"""

"""
checken of sdd's wel overeenkomen met cnf's
cnf = generateRandomCnf(2, 3, True)
for index, node in enumerate(cnf):
    print(f"node {index+1} =\t{node}")

compiler = SDDcompiler(cnf)
(sdd, sizeOfCnf) = compiler.compileToSdd()

with open("output/sdd.dot", "w") as out:
    print(sdd.dot(), file=out)"""



SizeVSClauseVar = {}
for i in [15, 20, 25]: #aantal vars
    print(f"i = {i}")
    for j in range(10, 5*i+1, 5): #aantal clauses
        print(f"j = {j}")
        sumOfSizes = 0
        ratio = j/i
        for k in range(10): #aantal repeats en dan gemiddelde berekenen 
            cnf = generateRandomCnf(j, i, True)

            compiler = SDDcompiler(cnf)
            (sdd, sizeOfCnf) = compiler.compileToSdd()
            sumOfSizes += sdd.size()
        
        if ratio in SizeVSClauseVar:
            SizeVSClauseVar[ratio].append(sumOfSizes/20)
        else:
            SizeVSClauseVar[ratio] = [sumOfSizes/20]
saveToPickle("output/explosionRateData.pickle", SizeVSClauseVar)