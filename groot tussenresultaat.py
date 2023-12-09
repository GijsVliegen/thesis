#dot -Tpng -sdd.png sdd.dot

""" een klein voorbeeld van hoe een tussenresultaat heel groot kan zijn tov het finale resultaat,
en ook hoe een ander tussenresultaat veel kleiner kan zijn"""

from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
import os
import graphviz

vtree = Vtree(var_count=4, var_order=[2, 1, 4, 3], vtree_type="right")
sdd = SddManager.from_vtree(vtree)
a, b, c, d = sdd.vars

# Build SDD for formula
a = SddManager.literal(sdd, 1)
NOTa = SddManager.literal(sdd, -1)
b = SddManager.literal(sdd, 2)
NOTb = SddManager.literal(sdd, -2)
c = SddManager.literal(sdd, 3)
NOTc = SddManager.literal(sdd, -3)
d = SddManager.literal(sdd, 4)
NOTd = SddManager.literal(sdd, -4)

f1 = a.disjoin(b)
f2 = a
f3 = NOTa.disjoin(c)
#f3 = c.conjoin(NOTa.disjoin(c))

f1f2 = sdd.apply(f1, f2, 0) #f1.conjoin(f2)
f1f3 = sdd.apply(f1, f3, 0)
f2f3 = f2.conjoin(f3)
final1 = f1f2.conjoin(f3)
final2 = f1f3.conjoin(f2)

print(f"grootte: f1 heeft size {SddNode.size(f1)} en {SddNode.count(f1)} nodes")
print(f"grootte: f2 heeft size {SddNode.size(f2)} en {SddNode.count(f2)} nodes")
print(f"grootte: f3 heeft size {SddNode.size(f3)} en {SddNode.count(f3)} nodes")
print(f"grootte: f1f2 heeft size {SddNode.size(f1f2)} en {SddNode.count(f1f2)} nodes")
print(f"grootte: f1f3 heeft size {SddNode.size(f1f3)} en {SddNode.count(f1f3)} nodes")
print(f"grootte: f2f3 heeft size {SddNode.size(f2f3)} en {SddNode.count(f2f3)} nodes")
print(f"grootte: final1 heeft size {SddNode.size(final1)} en {SddNode.count(final1)} nodes")
print(f"grootte: final2 heeft size {SddNode.size(final2)} en {SddNode.count(final2)} nodes")

output_directory = "/home/gijs/school/23-24/thesisUbuntu/output"

graphviz.Source(f1f3.dot()).render("output/f1f3", format='png')
graphviz.Source(f2f3.dot()).render("output/f2f3", format='png')
graphviz.Source(f1f2.dot()).render("output/f1f2", format='png')
graphviz.Source(f1.dot()).render("output/f1", format='png')
graphviz.Source(f2.dot()).render("output/f2", format='png')
graphviz.Source(f3.dot()).render("output/f3", format='png')
graphviz.Source(final1.dot()).render("output/final1", format='png')
graphviz.Source(final2.dot()).render("output/final2", format='png')

"""
# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Visualize SDD and Vtree
with open(file_path_sdd, "w") as out:
    print(f1.dot(), file=out)
with open(file_path_vtree, "w") as out:
    print(vtree.dot(), file=out)
print("einde programma")"""