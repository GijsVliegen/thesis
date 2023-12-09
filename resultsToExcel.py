import pickle, pprint
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from randomCNFGenerator import generateRandomCnf
from flatSDDCompiler import SDDcompiler
from thesis_files.propositional_formula import FormulaContainer
import matplotlib.pyplot as plt

def load_formula_from_pickle(filename: str) -> FormulaContainer:
    with open(filename, "rb") as f:
        formula = pickle.load(f)
    return formula

results = load_formula_from_pickle("output/differentSizesToStaticSddAND.pickle")

# Plot the range of integers for each key
for key, values in results.items():
    plt.plot(range(len(values)), values, label=key)

# Add labels and a legend
plt.xlabel('Index')
plt.ylabel('Integer Value')
plt.legend()

# Show the plot
plt.show()
plt.savefig("results/differentSizesToStaticSddAND.pickle")
