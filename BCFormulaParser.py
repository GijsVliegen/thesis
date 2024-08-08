from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from problog_formulas.propositional_formula import FormulaContainer, FormulaOp, RefFormula
import random, time
from flatSDDCompiler import SDDcompiler
from heuristicApplier import HeuristicApply, SddVarAppearancesList, SddVtreeCountList, heuristicApplyCustom
from heuristicApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, EL, VP_EL, ELVAR, VP_ELVAR, IVO_RL_EL, IVO_RL_EL_Size, \
    OR, AND

def parseBCToFormula(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    TrueStmts = [] #om als laatste te behandelen
    subFormulaDict = {}
    formula = FormulaContainer()
    varCounter = 0
    lineNr = -1
    while lineNr < len(lines)-1:
        lineNr += 1
        i = lines[lineNr]
        i = i[:-1]  #removes \n
        if i[0] == "T":
            TrueStmts.append(i[2:])
            # print(i[2:-1])
        if i[0] == "I":
            # print(i[2:-1])
            subFormulaDict[i[2:]] = len(subFormulaDict) + 1
            formula.add_formula(RefFormula(FormulaOp.ATOM, tuple()))
            varCounter += 1
        if i[0] == "G":
            gName, rest = i[2:].split(" := ")
            children = []
            handleLater = False
            for childName in rest[2:].split(" "):
                if childName in subFormulaDict:
                    childInt = subFormulaDict[childName]
                elif childName.startswith("-") and childName[1:] in subFormulaDict:
                    childInt = subFormulaDict[childName[1:]]
                    subFormulaDict[childName] = len(subFormulaDict) + 1#placeholder for neg formula
                    childInt = formula.add_formula(RefFormula(FormulaOp.NEG, tuple([childInt])))
                else:     #ongekende variable als kind
                    # childInt = subFormulaDict[childName]
                    handleLater = True
                    break
                children.append(childInt)

            if (handleLater):
                lines.append(i+"#")
                # print(f"variable {gName} handled later")
                continue

            subFormulaDict[gName] = len(subFormulaDict) + 1
            if rest[0] == "A" or rest[0] == "I":
                formula.add_formula(RefFormula(FormulaOp.CONJ, tuple(children)))
            if rest[0] == "O":
                formula.add_formula(RefFormula(FormulaOp.DISJ, tuple(children)))
        
    if (len(TrueStmts) == 0):
        return formula, len(formula), varCounter 
    finalChildren = []
    for childName in TrueStmts:
        if childName in subFormulaDict:
            finalChildren.append(subFormulaDict[childName])
        elif childName.startswith("-") and childName[1:] in subFormulaDict:
            childInt = subFormulaDict[childName[1:]]
            negChild = formula.add_formula(RefFormula(FormulaOp.NEG, tuple([childInt])))
            subFormulaDict[childName] = negChild #placeholder for neg formula
            finalChildren.append(negChild)
    lastNode = formula.add_formula(RefFormula(FormulaOp.CONJ, tuple(finalChildren)))
    return formula, lastNode, varCounter

class Compiler():
    def __init__(self, formula, sddManager, nrOfVars, heuristic):
        self.dynamicCache = {}
        self.formula = formula
        self.sddManager = sddManager
        self.nrOfVars = nrOfVars 
        self.heur = heuristic
    
    def clean(self, sdd):
        if sdd is not None: sdd.ref()
        self.sddManager.garbage_collect()
        if sdd is not None: sdd.deref()


    def compileToSdd(self, rootNodeId):
        rootNode = self.formula.get_formula(rootNodeId)
        if(rootNodeId in self.dynamicCache):
            return (self.dynamicCache[rootNodeId], 0, 0)
        
        if(rootNode.op == FormulaOp.ATOM):
            return (self.sddManager.literal(rootNodeId), 0, 0)
        if(rootNode.op == FormulaOp.NEG): #neg telt niet mee tot het aantal elementen in de DAG imo
            (sdd, totalTime, noOverheadTime) = self.compileToSdd(rootNode.children[0])
            negSdd = self.sddManager.negate(sdd)
            return (negSdd, totalTime, noOverheadTime)
        childrenSdd, compileTimes, noOverheadTimes = map(list, zip(*map(
                lambda childID: self.compileToSdd(childID), rootNode.children)))
        # childrenSdd = list(map(lambda childID: compileToSdd(formula, childID, sddManager, nrOfVars), rootNode.children))
        operationInt = AND if rootNode.op == FormulaOp.CONJ else OR

        (sdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = \
                heuristicApplyCustom(childrenSdd, self.nrOfVars, operationInt, self.heur, self.sddManager)
        
        self.dynamicCache[rootNodeId] = sdd
        return (sdd, sum(compileTimes) + totalTime, sum(noOverheadTimes) + noOverheadTime)


import os, signal
def folderIterator(folderPath, timeOut, heur):
    class TimeoutError(Exception):
            pass

    def timeout_handler(signum, frame):
        # raise TimeoutError("ran out of time, return a move now!")
        raise TimeoutError()

    def func_with_timeout(default_value):
        def decorator(func):
            def wrapper(*args, **kwargs):
                signal.signal(signal.SIGVTALRM, timeout_handler)  # Use SIGVTALRM instead of SIGALRM
                signal.setitimer(signal.ITIMER_VIRTUAL, timeOut, 0)  # Set a timeout alarm
                try:
                    result = func(*args, **kwargs)
                except TimeoutError:
                    # print("Timeout reached, returning")
                    result = default_value
                finally:
                    signal.setitimer(signal.ITIMER_VIRTUAL, 0)  # Cancel the alarm
                return result
            return wrapper
        return decorator

    @func_with_timeout(default_value=-1)
    def parseAndCompile(filePath):
        formula, lastNodeNr, var_count = parseBCToFormula(filePath)
        # print("parsed")
        vtree = Vtree(var_count, var_order=list(range(1,var_count+1)), vtree_type="balanced")
        mgr1 = SddManager.from_vtree(vtree)
        applier = HeuristicApply.getBaseApplier()
        try:
            compiler = Compiler(formula, mgr1, var_count, heur)
            sdd, compTime, timeNoOverhead = compiler.compileToSdd(lastNodeNr)
        except Exception as e:
            # print(f"An error occurred: {e}")
            x = 5
        else:
            result = (sdd, compTime, timeNoOverhead)
            return result
        
    def iterate_files_in_folder(folder_path):
        for root, dirs, files in os.walk(folder_path):
            # allFiles = sorted(files)
            # print(len(allFiles))
            # file_path = os.path.join(root, allFiles[id])
            # result = parseAndCompile(file_path)
            # return result
            for index, file in enumerate(sorted(files)):
                filePath = os.path.join(root, file)
                print(f"{index}: {filePath}")
                # formula, lastNodeNr, var_count = parseBCToFormula(filePath)
                # lenOfForm = len(formula._formulas)
                # formula._formulas[0].children
                # childrenListLengthsFirst = list(map(lambda form: len(form.children), formula._formulas[:-1]))
                # childrenListLengths = [x for x in childrenListLengthsFirst if x!=0]
                # maxChildNr = max(childrenListLengths)

                # print(f"formLength = {len(childrenListLengths)}, nodes with 2 children = {list(childrenListLengths).count(2)}")
                # print(f"max nr Of Children = {maxChildNr}")
                # if maxChildNr < 4 or lenOfForm < 100 or lenOfForm > 1000:
                #     try:
                #         # Remove the file
                #         os.remove(filePath)
                #         print(f"File {filePath} deleted successfully.")
                #     except Exception as e:
                #         print(f"Error occurred while deleting file {filePath}: {e}")
                # sdd = parseAndCompile(file_path)
            
    return iterate_files_in_folder(folderPath)

#werkt enkel op 3-cnf input
def cnfValidation(filePath, var_count):
    vtree = Vtree(var_count, var_order=list(range(1,var_count+1)), vtree_type="balanced")
    mgr = SddManager.from_vtree(vtree)
    sdd = mgr.read_cnf_file(bytes(filePath, encoding='utf-8'))
    return sdd

def testCircuit(folder_path, heur, id):
    data_directory = os.environ.get("VSC_DATA")
    if data_directory is None:
        data_directory = ""
    fullFolderPath = os.path.join(data_directory, folder_path)
    for root, dirs, files in os.walk(fullFolderPath):
        allFiles = sorted(files)
        print(len(allFiles))
        print(allFiles[id])
        filePath = os.path.join(root, allFiles[id])
        try:
            formula, lastNodeNr, var_count = parseBCToFormula(filePath)
        except Exception as e:
            print(f"An error occurred: {e}")
        else:
            print("parsed")
            vtree = Vtree(var_count, var_order=list(range(1,var_count+1)), vtree_type="balanced")
            mgr1 = SddManager.from_vtree(vtree)
            compiler = Compiler(formula, mgr1, var_count, heur)
            (sdd, compTime, timeNoOverhead) = compiler.compileToSdd(lastNodeNr)
            compiler.clean(sdd)

            print(f"final size = {sdd.size()}, compileTime = {compTime}, woOH = {timeNoOverhead}")
                # checking cnf, werkt niet, want moet in 3-cnf staan
                # splitPath = filePath.split("/")
                # cnfPath = splitPath[0] + "/dimacs/" + splitPath[2][:-3] + ".cnf"
                # cnfSdd = cnfValidation(cnfPath, var_count)
                # print(f"cnf compile size = {cnfSdd.size()}")

            data_directory = os.environ.get("VSC_DATA")
            if data_directory is None:
                data_directory = ""
            local_file_path = f"outputPaper/{allFiles[id][:-3]}/{heur}.txt"
            fullPath = os.path.join(data_directory, local_file_path)
            os.makedirs(os.path.dirname(fullPath), exist_ok=True)
            with open(fullPath, 'w') as file:
                file.write(f"{compTime} {timeNoOverhead}\n") 
            
#549 files
# def main():
#     # testCircuit("circuits/bcs/noisy_or_10.bc")
#     folder_path = 'circuits/bcs'
#     id = 5
#     testCircuit(folder_path, RANDOM, id)
#     # print(f"final size = {sdd.size()}, compileTime = {compTime}, woOH = {timeNoOverhead}")
#     testCircuit(folder_path, VP_EL, id)
#     # print(f"final size = {sdd.size()}, compileTime = {compTime}, woOH = {timeNoOverhead}")

import sys
def main():
    # folder_path = 'circuits/bcs'
    # folderIterator(folder_path, 5, 8)
    args = sys.argv[1:]
    heur = int(args[0])
    id = int(args[1])
    print(f"id = {id}, heur = {heur}")
    folder_path = 'circuits/bcs'
    testCircuit(folder_path, heur, id)

if __name__ == "__main__":
    # Call main function with command line arguments excluding script name
    main()