
from thesis_files.propositional_formula import FormulaContainer, FormulaOp, RefFormula
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode

class SDDcompiler:

    def __init__(self, nrOfVars, sddManager = None, vtree_type = "balanced"):

        self.sddManager = sddManager
        if self.sddManager is None:
            vtree = Vtree(var_count=nrOfVars, vtree_type=vtree_type) #kan nog aangepast worden voor experiment
            self.sddManager = SddManager.from_vtree(vtree)
        self.literalSdds = {}


    """
    compiled vanaf een rootnode de formule naar een sdd, werkt recursief

    best in deze functie de heuristiek inbouwen dmv apply_total functie te veranderen/vervangen"""
    def compileToSdd(self, formula, rootNodeId = -1):
        if rootNodeId == -1:
            rootNodeId = len(formula)
            self.literalSdds = {}
            for i in range(1, len(formula)+1):
                refFor = formula.get_formula(i)
                if refFor.op == FormulaOp.ATOM:
                    self.literalSdds[i] = self.sddManager.literal(i)

        rootNode = formula.get_formula(rootNodeId)
        #print(f"children of this node are {rootNode.children}")
        if(rootNode.op == FormulaOp.ATOM):
            return (self.literalSdds[rootNodeId], 1)
        
        if(rootNode.op == FormulaOp.NEG): #neg telt niet mee tot het aantal elementen in de DAG imo
            childNode = (formula).get_formula(rootNode.children[0])
            (sdd, totalNodesInDag) = self.compileToSdd(formula, rootNode.children[0])
            return (self.sddManager.negate(sdd), totalNodesInDag)

        childrenSdd, sizeOfChildrenDag = map(list, zip(*map(lambda child: self.compileToSdd(formula, child), rootNode.children)))
        
        #is de operatie conjoin (0) of disjoin (1)
        operationInt = 0 if rootNode.op == FormulaOp.CONJ else 1
        
        while len(childrenSdd) > 1:
            sdd1 = childrenSdd.pop(0)
            sdd2 = childrenSdd.pop(0)
            newSdd = self.sddManager.apply(sdd1, sdd2, operationInt)
            childrenSdd.append(newSdd)
        
        return (childrenSdd[0], sum(sizeOfChildrenDag) + 1)
