"""measures how much the comp time is after applying one constant sdd, with a range of different other sdd's"""
import pickle, pprint
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from randomCNFGenerator import generateRandomCnf
from flatSDDCompiler import SDDcompiler
from thesis_files.propositional_formula import FormulaContainer
import matplotlib.pyplot as plt
import timeit

operation = "AND"
operationInt = 0 if operation == "AND" else 1
nrOfIterations = 200 #laag zetten om te testen, uiteindelijk naar 100/500 ofzo zetten
nrOfVars = 20 #als deze verandert, ook staticCnf opnieuw genereren
cnf3 = True #true -> randome 3-cnf formule, false -> random n-cnf formule, met n tussen 1 en nrOfVars

#dot -Tpng -O sdd.dot

def saveToPickle(filename, data):

    with open(filename, 'wb') as file:
        # Use pickle.dump() to serialize and save the object to the file
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

def load_formula_from_pickle(filename: str) -> FormulaContainer:
    with open(filename, "rb") as f:
        formula = pickle.load(f)
    return formula

compiler = SDDcompiler(nrOfVars=20)
staticCnf = load_formula_from_pickle("output/staticCnf.pickle")
(staticSdd, sizeOfStaticCnf) = compiler.compileToSdd(staticCnf)

results = []
def applyStaticWithRandomSdd(nrOfClauses, nrOfVars):
    nextCnf = generateRandomCnf(i, nrOfVars, True)
    (nextSdd, sizeOfCnf) = compiler.compileToSdd(nextCnf)
    appliedSdd = compiler.sddManager.apply(nextSdd, staticSdd, operationInt)

x_values = [1, 2, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100]
for j in range(nrOfIterations):

    # Measure execution time (in seconds)
    results.append([])
    for i in x_values:
        timer = timeit.Timer(stmt=lambda: applyStaticWithRandomSdd(i, nrOfVars))
        execution_time = timer.timeit(number=1)
        results[j].append(execution_time)

print(f"OGgrootte = {staticSdd.size()}")

text3cnf = "3cnf" if cnf3 else ""
saveToPickle(f"output/differentSizesToStaticSdd{operation}{text3cnf}.pickle", results)

# Create a Timer object


# Plot the range of integers for each key
for one_iter in results:
    plt.plot(x_values, one_iter, 'o', label=i) 

# Add labels and a legend
plt.yscale('log')
plt.xlabel('nrOfClauses')
plt.ylabel('total size values')

# Show the plot
plt.show()
plt.savefig(f"results/variationCompTime{operation}.png")


"""
#code om staticSdd te genereren
staticCnf = generateRandomCnf(50, nrOfVars) #ratio clause/variable is 2.5
compiler = SDDcompiler(staticCnf)
(staticSdd, sizeOfCnf) = compiler.compileToSdd()
while staticSdd.size() == 0:
    staticCnf = generateRandomCnf(50, nrOfVars) #ratio clause/variable is 2.5
    compiler = SDDcompiler(staticCnf)
    (staticSdd, sizeOfCnf) = compiler.compileToSdd()
saveToPickle("output/staticCnf.pickle", staticCnf)
"""