#dot -Tpng -sdd.png sdd.dot

from randomOrderApplier import RandomOrderApply
import os

nrOfSdds=10
nrOfVars=20
nrOfClauses=10

randomApplier = RandomOrderApply(nrOfSdds, nrOfVars, nrOfClauses, cnf3=True, operation="OR")
sdd = randomApplier.doRandomApply(randomApplier.loadBaseSdds())

print(f"grootte: sdd heeft size {sdd.count()} en {randomApplier.compiler.sddManager.count()} nodes in de sddManager")

output_directory = "/home/gijs/school/23-24/thesisUbuntu/output"
file_path_vtree1 = os.path.join(output_directory, "vtree1.dot")
with open(file_path_vtree1, "w") as out:
    print(randomApplier.compiler.sddManager.vtree().dot(), file=out)

randomApplier.minimize_final_vtree()
sdd = randomApplier.doRandomApply(randomApplier.loadBaseSdds())
file_path_vtree2 = os.path.join(output_directory, "vtree2.dot")
with open(file_path_vtree2, "w") as out:
    print(randomApplier.compiler.sddManager.vtree().dot(), file=out)

print(f"grootte: sdd heeft size {sdd.count()} en {randomApplier.compiler.sddManager.count()} nodes in de sddManager")

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
