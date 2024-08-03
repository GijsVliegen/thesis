from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from problog_formulas.propositional_formula import FormulaContainer, FormulaOp, RefFormula
import random
from flatSDDCompiler import SDDcompiler
from heuristicApplier import HeuristicApply, SddVarAppearancesList, SddVtreeCountList
from heuristicApplier import RANDOM, IVO_LR, IVO_RL, \
    KE, VP, VP_KE, VO, EL, VP_EL, ELVAR, VP_ELVAR, IVO_RL_EL, IVO_RL_EL_Size

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
                print(f"variable {gName} handled later")
                continue

            subFormulaDict[gName] = len(subFormulaDict) + 1
            if rest[0] == "A" or rest[0] == "I":
                formula.add_formula(RefFormula(FormulaOp.CONJ, tuple(children)))
            if rest[0] == "O":
                formula.add_formula(RefFormula(FormulaOp.DISJ, tuple(children)))
        

    
    finalChildren = []
    for childName in TrueStmts:
        finalChildren.append(subFormulaDict[childName])
    lastNode = formula.add_formula(RefFormula(FormulaOp.CONJ, tuple(finalChildren)))
    return formula, lastNode, varCounter

def main():

    formula, lastNodeNr, var_count = parseBCToFormula("circuits/bcs/raki_gh_3_prob.bc")
    vtree = Vtree(var_count, var_order=list(range(1,var_count+1)), vtree_type="balanced")
    mgr1 = SddManager.from_vtree(vtree)
    compiler1 = SDDcompiler(var_count, mgr1)
    applier = HeuristicApply.getBaseApplier()
    (sdd1, _) = compiler1.compileToSddHeuristic(formula, lastNodeNr, RANDOM, applier)
    print(sdd1.size())

main()