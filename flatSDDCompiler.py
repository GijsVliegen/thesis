
from problog_formulas.propositional_formula import FormulaContainer, FormulaOp, RefFormula
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
CONJUNCTIE = 0
DISJUNCTIE = 1

class SDDcompiler:

    def __init__(self, nrOfVars, sddManager = None, vtree_type = "balanced", vtree = 0):
        self.nrOfVars = nrOfVars
        self.sddManager = sddManager
        if self.sddManager is None:
            print("oei! alert!")
            vtree = Vtree(var_count=nrOfVars, vtree_type=vtree_type) #kan nog aangepast worden voor experiment
            self.sddManager = SddManager.from_vtree(vtree)

    def changeVtree(self, vtree):
        self.sddManager = SddManager.from_vtree(vtree)

    """
    compiled vanaf een rootnode de formule naar een sdd, werkt recursief

    best in deze functie de heuristiek inbouwen dmv apply_total functie te veranderen/vervangen"""
    def compileToSdd(self, formula, rootNodeId, sddManager):
        rootNode = formula.get_formula(rootNodeId)
        if(rootNode.op == FormulaOp.ATOM):
            return (sddManager.literal(rootNodeId), 1)
        if(rootNode.op == FormulaOp.NEG): #neg telt niet mee tot het aantal elementen in de DAG imo
            (sdd, totalNodesInDag) = self.compileToSdd(formula, rootNode.children[0], sddManager)
            return (sddManager.negate(sdd), totalNodesInDag)
        childrenSdd, sizeOfChildrenDag = map(list, zip(*map(lambda child: self.compileToSdd(formula, child, sddManager), rootNode.children)))
        operationInt = CONJUNCTIE if rootNode.op == FormulaOp.CONJ else DISJUNCTIE
        while len(childrenSdd) > 1:
            sdd1 = childrenSdd.pop(0)
            sdd2 = childrenSdd.pop(0)
            newSdd = sddManager.apply(sdd1, sdd2, operationInt)
            childrenSdd.append(newSdd)
        return (childrenSdd[0], sum(sizeOfChildrenDag) + 1)
    

    #TODO: add dynamyic programming: store noteID + sdd als ooit gecompileerd, aangezien we met DAGs werken
    def compileToSddHeuristic(self, formula, rootNodeId, heuristic, applier):
        rootNode = formula.get_formula(rootNodeId)
        if(rootNode.op == FormulaOp.ATOM):
            return (self.sddManager.literal(rootNodeId), 1)
        if(rootNode.op == FormulaOp.NEG): #neg telt niet mee tot het aantal elementen in de DAG imo
            (sdd, totalNodesInDag) = self.compileToSddHeuristic(formula, rootNode.children[0], heuristic, applier)
            return (self.sddManager.negate(sdd), totalNodesInDag)
        childrenSdds, sizeOfChildrenDag = map(list, 
                    zip(*map(lambda child: self.compileToSddHeuristic(formula, child, heuristic, applier), rootNode.children)))
        operationInt = CONJUNCTIE if rootNode.op == FormulaOp.CONJ else DISJUNCTIE
        
        applier.setManuelApply(childrenSdds, self.nrOfVars, operationInt)
        (sdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = applier.doHeuristicApply(heuristic, timeOverhead = True) #true -> overhead erbij

        return (sdd.getSdd(), sum(sizeOfChildrenDag) + 1)
