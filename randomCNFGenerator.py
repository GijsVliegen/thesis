from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from thesis_files.propositional_formula import FormulaContainer, FormulaOp, RefFormula
import random

def generateRandomCnfDimacs(nrOfVars, nrOfClauses, cnf3 = True):
    cnf_formula = []
    # Generate random CNF clauses
    for _ in range(nrOfClauses):

        lengthOfClause = random.randint(1, nrOfVars) if not cnf3 else 3
        clause = []
        while len(clause) != lengthOfClause:
            newVar = random.randint(1, nrOfVars)
            #ofwel de pos ofwel de neg var toevoegen, beide heeft geen zin
            if newVar not in clause and -newVar not in clause:
                if random.choice([True, False]):
                    clause.append(newVar)
                else:
                    clause.append(-newVar)
            clause.sort()
        cnf_formula.append(clause)
    return getAsDimacsString(cnf_formula, nrOfVars)

def getAsDimacsString(cnf_formula,  nrOfVars):
    string = f'p cnf {nrOfVars} {len(cnf_formula)}'
    for clause in cnf_formula:
        string += '\n' + ' '.join(map(str, clause)) + ' 0'
    return string


def generateRandomCnfFormula(nrOfClauses, nrOfVars, cnf3 = False):

    formula = FormulaContainer()

    for i in range(1, nrOfVars+1):
        formula.add_formula(RefFormula(FormulaOp.ATOM, tuple()))
    
    for i in range(1, nrOfVars+1):
        formula.add_formula(RefFormula(FormulaOp.NEG, tuple([i])))

    beginIndexClauses = len(formula) + 1

    for j in range(nrOfClauses):
        varsForThisClause = set()

        lengthOfClause = random.randint(1, nrOfVars) if not cnf3 else 3
        while len(varsForThisClause) != lengthOfClause:
            newVar = random.randint(1, nrOfVars)
            #ofwel de pos ofwel de neg var toevoegen, beide heeft geen zin
            if newVar not in varsForThisClause and -newVar not in varsForThisClause:
                if random.choice([True, False]):
                    varsForThisClause.add(newVar)
                else:
                    varsForThisClause.add(-newVar)
        children = []
        for var in varsForThisClause:
            if var < 0: children.append(var*-1 + nrOfVars)
            else: children.append(var)
        formula.add_formula(RefFormula(FormulaOp.DISJ, tuple(sorted(children))))
    
    endIndexClauses = len(formula) + 1

    formula.add_formula(RefFormula(FormulaOp.CONJ, tuple(range(beginIndexClauses, endIndexClauses))))
    return formula
"""
formula = generateRandomCnf(40, 10, True)
print(f"Number of variables: {formula.get_nb_vars()}")
for index, node in enumerate(formula):
    print(f"node {index+1} =\t{node}")"""