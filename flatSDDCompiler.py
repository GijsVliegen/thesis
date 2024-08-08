
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
        self.dynamicCache = {}
    
    def changeVtree(self, vtree):
        self.sddManager = SddManager.from_vtree(vtree)

    """
    compiled vanaf een rootnode de formule naar een sdd, werkt recursief

    best in deze functie de heuristiek inbouwen dmv apply_total functie te veranderen/vervangen"""
    def compileToSdd(self, formula, rootNodeId, sddManager):
        rootNode = formula.get_formula(rootNodeId)
        if(rootNode.op == FormulaOp.ATOM):
            return sddManager.literal(rootNodeId)
        if(rootNode.op == FormulaOp.NEG): #neg telt niet mee tot het aantal elementen in de DAG imo
            sdd = self.compileToSdd(formula, rootNode.children[0], sddManager)
            return sddManager.negate(sdd)
        childrenSdd = list(map(lambda child: self.compileToSdd(formula, child, sddManager), rootNode.children))
        operationInt = CONJUNCTIE if rootNode.op == FormulaOp.CONJ else DISJUNCTIE

        while len(childrenSdd) > 1:
            sdd1 = childrenSdd.pop(0)
            sdd2 = childrenSdd.pop(0)
            newSdd = sddManager.apply(sdd1, sdd2, operationInt)
            childrenSdd.append(newSdd)
        return childrenSdd[0]
    

    #TODO: add dynamyic programming: store noteID + sdd als ooit gecompileerd, aangezien we met DAGs werken
    def compileToSddHeuristic(self, formula, rootNodeId, heuristic, applier):
        rootNode = formula.get_formula(rootNodeId)
        if(rootNodeId in self.dynamicCache):
            return self.dynamicCache[rootNodeId]
        
        if(rootNode.op == FormulaOp.ATOM):
            sdd = self.sddManager.literal(rootNodeId)
            self.dynamicCache[rootNodeId] = sdd 
            return sdd
        if(rootNode.op == FormulaOp.NEG): #neg telt niet mee tot het aantal elementen in de DAG imo
            sdd = self.sddManager.negate(self.compileToSddHeuristic(formula, rootNode.children[0], heuristic, applier))
            self.dynamicCache[rootNodeId] = sdd
            return sdd
        childrenSdds = list(map(lambda child: self.compileToSddHeuristic(formula, child, heuristic, applier), rootNode.children))
        operationInt = CONJUNCTIE if rootNode.op == FormulaOp.CONJ else DISJUNCTIE
        
        if (len(childrenSdds) == 1):
            return childrenSdds[0]
        applier.setManuelApply(childrenSdds, self.nrOfVars, operationInt)
        (sdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = applier.doHeuristicApply(heuristic, timeOverhead = True) #true -> overhead erbij
        print(f"rootnodeId = {rootNodeId}, sdd = {sdd}, size = {sdd.size()}")
        print(f"cache = {self.dynamicCache}")
        self.dynamicCache[rootNodeId] = sdd
        return sdd
