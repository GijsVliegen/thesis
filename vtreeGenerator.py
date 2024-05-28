from randomCNFGenerator import generateRandomCnfFormula
from flatSDDCompiler import SDDcompiler
from pysdd.sdd import Vtree
import random
import os
import sys
import gc
import time
import graphviz

def oneVtreeGenerator(nrOfVars, nr):
    data_directory = os.environ.get("VSC_DATA")
    if data_directory is None:
        data_directory = ""
    vars = list(range(1, nrOfVars+1))
    random.shuffle(vars)
    vtree = Vtree(nrOfVars, vars, "random")
    local_file_path = f"randomVtrees/vtree_{nr}.txt"
    fullPath = os.path.join(data_directory, local_file_path)
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)
            
    vtree.save(bytes(fullPath, encoding="utf-8"))
    # graphviz.Source(vtree.dot()).render(f"randomVtrees/dotvtree_{i}", format='png')
    print(f"vars left = {vtree.left().var_count()}, vars right = {vtree.right().var_count()}")


def randomVtreeGenerator(nrOfVars, iters):
    for i in range(iters):
        time.sleep(1)
        oneVtreeGenerator(nrOfVars, i)

randomVtreeGenerator(12, 5) 