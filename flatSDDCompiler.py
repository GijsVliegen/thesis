
from problog_formulas.propositional_formula import FormulaContainer, FormulaOp, RefFormula
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
CONJUNCTIE = 0
DISJUNCTIE = 1

class SDDcompiler:

    def __init__(self, nrOfVars, sddManager = None, vtree_type = "balanced", vtree = 0):

        self.sddManager = sddManager
        if self.sddManager is None:
            vtree = Vtree(var_count=nrOfVars, vtree_type=vtree_type) #kan nog aangepast worden voor experiment
            self.sddManager = SddManager.from_vtree(vtree)

    def changeVtree(self, vtree):
        self.sddManager = SddManager.from_vtree(vtree)

    """
    compiled vanaf een rootnode de formule naar een sdd, werkt recursief

    best in deze functie de heuristiek inbouwen dmv apply_total functie te veranderen/vervangen"""
    def compileToSdd(self, formula, rootNodeId):
        rootNode = formula.get_formula(rootNodeId)
        if(rootNode.op == FormulaOp.ATOM):
            return (self.sddManager.literal(rootNodeId), 1)
        if(rootNode.op == FormulaOp.NEG): #neg telt niet mee tot het aantal elementen in de DAG imo
            (sdd, totalNodesInDag) = self.compileToSdd(formula, rootNode.children[0])
            return (self.sddManager.negate(sdd), totalNodesInDag)
        childrenSdd, sizeOfChildrenDag = map(list, zip(*map(lambda child: self.compileToSdd(formula, child), rootNode.children)))
        operationInt = CONJUNCTIE if rootNode.op == FormulaOp.CONJ else DISJUNCTIE
        while len(childrenSdd) > 1:
            sdd1 = childrenSdd.pop(0)
            sdd2 = childrenSdd.pop(0)
            newSdd = self.sddManager.apply(sdd1, sdd2, operationInt)
            childrenSdd.append(newSdd)
        return (childrenSdd[0], sum(sizeOfChildrenDag) + 1)
