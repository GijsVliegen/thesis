from randomCNFGenerator import generateRandomCnfFormula, generateRandomCnfDimacs
from flatSDDCompiler import SDDcompiler
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode, SddManager
import random
import timeit
import ctypes

SMALLEST_FIRST = 1
VTREESPLIT = 2
VTREESPLIT_WITH_SMALLEST_FIRST = 3
VTREE_VARIABLE_ORDERING = 4
ELEMENT_UPPERBOUND = 5
INVERSE_VAR_ORDER_LR = 6
INVERSE_VAR_ORDER_RL = 7
RANDOM = 99
OR = 1
AND = 0

#uitbreiding van List met functies:
    # getNextSddsToApply() -> moet geïmplementeerd worden, 
    # _insert(), 
    # __getitem__(), 
    # update()  
class ExtendedList(list):
    def __init__(self, sdds):
        super().__init__()
        for i in sdds:
            self.append(i)
    def update(self, newSdd): #gebruikt in eigen code
        self.append(newSdd)
    def getNextSddsToApply(self):
        return self.pop(0), self.pop(0)
    def __getitem__(self, index):
        return super().__getitem__(index)
    def _insert(self, index, newSddSize): #inserts object thats already of right type
        super().insert(index, newSddSize)

#kiest telkens 2 random sdds uit de list 
class RandomList(ExtendedList):
    def __init__(self, sdds):
        super().__init__(sdds)
    def getNextSddsToApply(self):
        firstInt = random.randint(0, len(self)-1)
        firstSdd = self[firstInt]
        secondInt = firstInt
        while (secondInt == firstInt):
            secondInt = random.randint(0, len(self)-1)
        secondSdd = self[secondInt]
        if firstInt > secondInt:
            self.remove(firstSdd)
            self.remove(secondSdd)
        else:
            self.remove(secondSdd)
            self.remove(firstSdd)
        return firstSdd, secondSdd

#houdt een lijst bij van SddSize (achter de schermen), die gesorteerd zijn per size van de sdd 
class SddSizeList(ExtendedList):
    def __init__(self, sdds):
        super().__init__(sdds)
    def pop(self, index):
        return super().pop(index).getSdd()
    def insert(self, index, newSdd):       
        super().insert(index, self.SddSize(newSdd))
    def append(self, newSdd):
        super().append(self.SddSize(newSdd))
    def update(self, newSdd): 
        insort_right(self, self.SddSize(newSdd))
    
    class SddSize:
        def __init__(self, sdd):
            self.sdd = sdd
            self.size = sdd.size()
        def __lt__(self, other):
            return self.size < other.size
        def getSdd(self):
            return self.sdd

#houdt een lijst bij van sddVtreeCounts, de lijst van sdds is niet gesorteerd,
        #achter de schermen wordt een lijst van tupels bijgehouden (estimated size, sdd1, sdd2)
class SddVtreeCountList(ExtendedList):
    def __init__(self, sdds, sddManager):
        super().__init__([]) #roept append op voor elke sdd in 
        self.sizeEstimateTuples = ExtendedList([])
        self.vtreeRoot = sddManager.vtree()
        self.sddManager = sddManager
        for i in sdds:
            self.append(i)
    def pop(self, index):
        return super().pop(index).getSdd()
    def update(self, newSdd): 
        self.append(newSdd)

    def getNextSddsToApply(self):
        (_, sddVtreeCount1, sddVtreeCount2) = self.sizeEstimateTuples.pop(0)
        index = 0
        while index < len(self.sizeEstimateTuples):
            sizeEstimateTuple = self.sizeEstimateTuples[index]
            if (sddVtreeCount1 == sizeEstimateTuple[1] or sddVtreeCount1 == sizeEstimateTuple[2] or 
                sddVtreeCount2 == sizeEstimateTuple[1] or sddVtreeCount2 == sizeEstimateTuple[2]):
                del self.sizeEstimateTuples[index]
            else:
                index += 1
        self.remove(sddVtreeCount1)
        self.remove(sddVtreeCount2)
        return sddVtreeCount1.getSdd(), sddVtreeCount2.getSdd()
    # def pop(self, index):                 #onnuttig en onlgische functie voor deze structuur
    #     sdd = super().pop(index).getSdd()
    # def insert(self, index, newSdd):      #onnuttige en onlogische functie voor deze structuur
    #     super.insert(index, self.SddVtreeCount(newSdd))
    def append(self, newSdd):
        varList = self.sddManager.sdd_variables(newSdd)
        newSddVtreeCount = self.SddVtreeCount(newSdd, varList)
        for sddVtreeCount in self:
            newSizeEstimateTuple = (SddVtreeCountList._getUpperLimit(sddVtreeCount, newSddVtreeCount, self.vtreeRoot), sddVtreeCount, newSddVtreeCount)
            #newSizeEstimateTuple = (5, sddVtreeCount, newSddVtreeCount)
            #om een of andere reden werkt dit niet -> brute force insert
            insort_right(self.sizeEstimateTuples, newSizeEstimateTuple, key=lambda x: x[0])
        super().append(newSddVtreeCount)

    def _getUpperLimit(sddVtreeCount1, sddVtreeCount2, root):
        root1 = sddVtreeCount1.topVtreeNode
        root2 = sddVtreeCount2.topVtreeNode
        if (root1 is None):
            return sum(sddVtreeCount2.vtreeCount)
        if (root2 is None):
            return sum(sddVtreeCount1.vtreeCount)
        #root = Vtree.lca(root1, root2, root)
        queue = [root]
        tempVtreeCount1 = sddVtreeCount1.vtreeCount.copy()
        tempVtreeCount2 = sddVtreeCount2.vtreeCount.copy()
        extraFactorFound = False
        while len(queue) > 0 and not extraFactorFound: #veel simpelere implementatie die de volledige vtree overloopt
            nextVtreeNode = queue.pop(0)
            pos = nextVtreeNode.position()
            if (nextVtreeNode is None):
                print("iets geks met nextVtreeNode of root1 of root2, is None...")
            if (Vtree.is_sub(root1, nextVtreeNode.left()) and (Vtree.is_sub(nextVtreeNode, root2) or root2.position() > pos)): #sdd1 links van nextVtreeNode, nextVtreeNode onder sdd2
                extraFactorFound = True
                tempVtreeCount1 = sddVtreeCount1.addFactor2()
            if ((Vtree.is_sub(nextVtreeNode, root1) or root1.position() > pos) and Vtree.is_sub(root2, nextVtreeNode.left())): #sdd2 links van nextVtreeNode, nextVtreeNode onder sdd1
                extraFactorFound = True
                tempVtreeCount2 = sddVtreeCount2.addFactor2()
            if nextVtreeNode.left().is_leaf() != 1: #geen leafnode
                queue.append(nextVtreeNode.left())
            if nextVtreeNode.right().is_leaf() != 1: #geen leafnode
                queue.append(nextVtreeNode.right())

        newVtreeCount = []
        for (i,j) in zip(tempVtreeCount1, tempVtreeCount2):
            if i == 0 and j != 0: i = 1
            if i != 0 and j == 0: j = 1
            newVtreeCount.append(i*j)
        
        combinedVars = [int(x or y) for x,y in zip(sddVtreeCount1.varList, sddVtreeCount2.varList)]
        varsPerVtreeNode = SddVtreeCountList.varsUnderVtreeNode(combinedVars, root)
        newVtreeCount = SddVtreeCountList.extraUpperbound(newVtreeCount, varsPerVtreeNode, root)
            
        return sum(newVtreeCount)
    
    def extraUpperbound(vtreeCount, varsPerVtreeNode, root):
        queue = [root]    
        while len(queue) > 0: #veel simpelere implementatie die de volledige vtree overloopt
            currentNode = queue.pop(0)
            parentElCount = 1
            if (currentNode != root):
                parentElCount = vtreeCount[currentNode.parent().position()]
            if (not currentNode.is_leaf()): #geen rootnode -> nog hoger level
                queue.append(currentNode.left())
                queue.append(currentNode.right())
                varLimit = 2**(min(varsPerVtreeNode[currentNode.left().position()], 2**varsPerVtreeNode[currentNode.right().position()]))
                if vtreeCount[currentNode.position()] > parentElCount*varLimit:
                    #print(f"extra limiet was nuttig: eerst {vtreeCount[currentNode.position()]}, nu {parentElCount*varLimit}")
                    vtreeCount[currentNode.position()] = parentElCount*varLimit
        return vtreeCount

    def varsUnderVtreeNode(varList, vtreeNode, left = 0, right = 0):
        #als vtreeNode geen leaf is -> oneven positie
        #                   wel een leaf -> even positie
        #als vtreeNode positie 7 is, 4 variabelen links
        parent = vtreeNode.root()
        if (vtreeNode == parent):#rootnode
            left = 0
            right = len(varList)*2-1
        if vtreeNode.is_leaf() == 1: #leafnode
            return [varList[int(left/2)]]
        leftList = SddVtreeCountList.varsUnderVtreeNode(varList, vtreeNode.left(), left, vtreeNode.position())
        rightList = SddVtreeCountList.varsUnderVtreeNode(varList, vtreeNode.right(), vtreeNode.position() + 1, right)
        return leftList + [sum(varList[int(left/2): int((right+1)/2)])] + rightList
        
    class SddVtreeCount:
        def __init__(self, sdd, varList):
            self.sdd = sdd
            #self.vtreeCount = [0, 2, 0, 2, 0, 4, 4, 2, 4, 2, 0, 2, 4, 2] #zeker lang genoeg zodat er geen out of bounds access gebeurt
            self.vtreeCount = sdd.local_vtree_element_count()
            self.topVtreeNode = sdd.vtree()
            self.varList = varList
        
        def getSdd(self):
            return self.sdd
        
        def addFactor2(self):
            if (self.topVtreeNode is None): #sdd is True of False
                return self.vtreeCount.copy()
            #primes moeten partitie vormen -> sdd a wordt (a, True) (~a, False)
                    #negatie van a -> negatie van subs van a
                        #van elke sub negatie toevoegen -> ook maal 2 doen van aantal elementen
            tempVtreeCount = self.vtreeCount.copy()
            parentPos = self.topVtreeNode.parent().position()
            tempVtreeCount[parentPos] = max(2, 2*tempVtreeCount[parentPos])
            queue = [self.topVtreeNode]
            while len(queue) > 0:
                nextVtreeNode = queue.pop(0)
                if (nextVtreeNode.is_leaf() != 1):#geen leafnode
                    tempVtreeCount[nextVtreeNode.position()] = max(2, 2*tempVtreeCount[nextVtreeNode.position()])
                    queue.append(nextVtreeNode.right())
            return tempVtreeCount

#houdt een lijst bij van SddVarAppearance (achter de schermen), die gesorteerd zijn volgens de varpriority
class SddVarAppearancesList(ExtendedList):
    def __init__(self, sdds, sddManager, inverse = False, LR = True):
        self.var_order = self.getVarPriority(sddManager.vtree(), LR)
        if (inverse):
            self.var_order.reverse()
        self.sddManager = sddManager
        super().__init__(sdds)
    
    def pop(self, index):
        return super().pop(index).getSdd()
    def insert(self, index, newSdd):
        varList = self.sddManager.sdd_variables(newSdd)
        newSddVarAppearance = self.SddVarAppearance(newSdd, varList, self.var_order)
        super().insert(index, newSddVarAppearance)
    def append(self, newSdd):
        varList = self.sddManager.sdd_variables(newSdd)
        newSddVarAppearance = self.SddVarAppearance(newSdd, varList, self.var_order)
        super().append(newSddVarAppearance)
    def update(self, newSdd): #insert new element while keeping sortedness
        varList = self.sddManager.sdd_variables(newSdd)
        insort_right(self, self.SddVarAppearance(newSdd, varList, self.var_order))

    class SddVarAppearance:
        def __init__(self, sdd, varsUsed, varOrdering):
            self.sdd = sdd
            self.varsUsed = varsUsed
            self.varOrdering = varOrdering
        def __lt__(self, other):
            for i in self.varOrdering:
                if self.varsUsed[i-1] > other.varsUsed[i-1]: #als die een voorkomen heeft van een variabele hoog en links in de vtree en other niet -> sdd eerst zetten
                    return True
            return False
        def getSdd(self):
            return self.sdd
    
    #LR geeft aan of de vtree van links naar rechts of van rechts naar links moet doorlopen worden
    def getVarPriority(self, vtree, LR):
        varOrdering = []
        queue = [vtree]
        while len(queue) > 0:
            nextVtreeNode = queue.pop(0)
            if nextVtreeNode.is_leaf() == 1:
                varOrdering.append(nextVtreeNode.var())
            else:
                leftVtree = nextVtreeNode.left()
                rightVtree = nextVtreeNode.right()
                if (LR):
                    queue.append(leftVtree)
                    queue.append(rightVtree)
                else:
                    queue.append(rightVtree)
                    queue.append(leftVtree)
        return varOrdering
        #breadth first de vtree doorlopen, en dan de varOrder opslaan

#wordt gebruikt voor bepaalde list structuren
def insort_right(sortedList, newElement, key = lambda x: x, lo=0, hi=None):
    """Insert item x in list a, and keep it sorted assuming a is sorted.
    If x is already in a, insert it to the right of the rightmost x.
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    newElementVal = key(newElement)
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(sortedList)
    while lo < hi:
        mid = (lo + hi) // 2
        if newElementVal < key(sortedList[mid]):
            hi = mid
        else:
            lo = mid + 1
    sortedList._insert(lo, newElement)

class RandomOrderApply():

    def extractCounts(self):
        temp = self.nodeCounterList
        self.nodeCounterList = []
        return temp

    def renew(self):
        self.compiler.sddManager.garbage_collect()
        self.baseSdds = self.generateRandomSdds()

    def size(self):
        return self.compiler.sddManager.size()
    
    def collectMostGarbage(self, sdd = None):
        self.saveBaseSdds()
        if sdd is not None: sdd.ref()
        self.compiler.sddManager.garbage_collect()
        if sdd is not None: sdd.deref()
        self.unsaveBaseSdds()

    def collectAllGarbage(self):
        self.compiler.sddManager.garbage_collect()

    def __enter__(self):
        print(f" entry dead count = {self.compiler.sddManager.dead_count()}")
        return self #needed to return object to variable after 'as'
    def __exit__(self, exc_type, exc_value, traceback):
        print(f" exit dead count = {self.compiler.sddManager.dead_count()}")
        self.compiler.sddManager.garbage_collect()

    def __init__(self, nrOfSdds, nrOfVars, nrOfClauses, vtree_type = "balanced"):
        self.nrOfSdds = nrOfSdds
        self.nrOfVars = nrOfVars
        self.nrOfClauses = nrOfClauses
        self.cnf3 = True
        """
        AND operatie -> 10 keer 50 clauses: zelfde als een cnf met 500 clauses -> skewed result?
        """ 
        self.compiler = SDDcompiler(nrOfVars=nrOfVars, vtree_type=vtree_type)
        self.baseSdds = self.generateRandomSdds()
        self.nodeCounterList = []

    def generateRandomSdds(self):
        randomSdds = []
        for _ in range(self.nrOfSdds):
            cnf = generateRandomCnfFormula(self.nrOfClauses, self.nrOfVars, self.cnf3)
            (sdd, size) = self.compiler.compileToSdd(cnf, len(cnf))
            randomSdds.append(sdd)
        return randomSdds

    def saveBaseSdds(self):
        for baseSdd in self.baseSdds:
            baseSdd.ref()       
            
    def unsaveBaseSdds(self):
        for baseSdd in self.baseSdds:
            baseSdd.deref()
    
    def doApply(self, sdd1, sdd2, operation, timeOverhead):
        time = 0
        if not timeOverhead:
            startTime = timeit.default_timer()
            newSdd = self.compiler.sddManager.apply(sdd1, sdd2, operation)
            time += timeit.default_timer() - startTime
        else:
            newSdd = self.compiler.sddManager.apply(sdd1, sdd2, operation)
        return (newSdd, time)

    # SMALLEST_FIRST = 1
    # VTREESPLIT = 2
    # VTREESPLIT_WITH_SMALLEST_FIRST = 3
    # VTREE_VARIABLE_ORDERING = 4
    # ELEMENT_UPPERBOUND = 5
    # INVERSE_VAR_ORDER_LR = 6
    # INVERSE_VAR_ORDER_RL = 7
    # RANDOM = 99
    def getFirstDataStructure(self, sdds, heuristic):
        if heuristic == SMALLEST_FIRST:
            return SddSizeList(sdds)
        if heuristic == VTREE_VARIABLE_ORDERING:
            return SddVarAppearancesList(sdds, self.compiler.sddManager)
        if heuristic == INVERSE_VAR_ORDER_LR:
            return SddVarAppearancesList(sdds, self.compiler.sddManager, inverse=True)
        if heuristic == INVERSE_VAR_ORDER_RL:
            return SddVarAppearancesList(sdds, self.compiler.sddManager, inverse=True, LR=False)
        if heuristic == ELEMENT_UPPERBOUND:
            return SddVtreeCountList(sdds, self.compiler.sddManager)
        if heuristic == RANDOM:
            return RandomList(sdds)
        else: print(f"heuristiek {heuristic} is nog niet geïmpleneteerd")

    def doHeuristicApply2Recursive(self, parentVtreeNode, innerHeuristic, sdds, operation, timeOverhead):
        #recursively split up the children in left.children, right.children en middle.children
        # left children samen (recursief) applyen, dan right.children (recursief), en dan middle.children
        totalTime = 0
        if len(sdds) == 1:
            return (sdds[0], 0)
        if len(sdds) == 2:
            return self.doApply(sdds[0], sdds[1], operation, timeOverhead)
        if parentVtreeNode is None: #bijvoorbeeld omdat
            print("iets geks met parentVtreeNode, is None...")
        left = []
        right = []
        middle = []
        for sdd in sdds:
            if (sdd.vtree() is None):
                middle.append(sdd)
            elif Vtree.is_sub(sdd.vtree(), parentVtreeNode.left()):
                left.append(sdd)
            elif Vtree.is_sub(sdd.vtree(), parentVtreeNode.right()):
                right.append(sdd)
            else: #aan beide zijden -> middle
                middle.append(sdd)
        if len(left) > 0:
            (recursiveSdd, recursiveTime) = self.doHeuristicApply2Recursive(parentVtreeNode.left(), innerHeuristic, left, operation, timeOverhead)
            middle.append(recursiveSdd)
            totalTime += recursiveTime 
        if len(right) > 0:
            (recursiveSdd, recursiveTime) = self.doHeuristicApply2Recursive(parentVtreeNode.right(), innerHeuristic, right, operation, timeOverhead)
            middle.append(recursiveSdd)
            totalTime += recursiveTime
        (resultSdd, extraTime) = self.doHeuristicApplySdds(innerHeuristic, middle, operation, timeOverhead)
        return (resultSdd, totalTime + extraTime)

    def doHeuristicApplySdds(self, heuristic, sdds, operation, timeOverhead): #base value zou moeten veranderd worden naar de beste heuristiek
        #print(f"nu: using heuristic {heuristic}")
        totalTime = 0
        datastructure = self.getFirstDataStructure(sdds, heuristic)
        while len(datastructure) > 1:
            sdd1, sdd2 = datastructure.getNextSddsToApply()
            (newSdd, applytime) = self.doApply(sdd1, sdd2, operation, timeOverhead)
            totalTime += applytime
            datastructure.update(newSdd)
            #self.nodeCounterList.append(self.compiler.sddManager.dead_size())
            # self.nodeCounterList.append((self.compiler.sddManager.count(), self.compiler.sddManager.live_count(), self.compiler.sddManager.dead_count())) #count, dead_count of live_count
            #doSomethingWithResults(rootNodeId, rootNode, newSdd, datastructure)
        finalSdd = datastructure.pop(0)
        return (finalSdd, totalTime)

    def doHeuristicApply(self, heuristic, operation, timeOverhead = True):
        #print(f"using heuristic {heuristic}")
        if heuristic == VTREESPLIT:
            (result, time) = self.doHeuristicApply2Recursive(self.compiler.sddManager.vtree(), RANDOM, self.baseSdds, operation, timeOverhead)
        elif heuristic == VTREESPLIT_WITH_SMALLEST_FIRST:
            (result, time) = self.doHeuristicApply2Recursive(self.compiler.sddManager.vtree(), SMALLEST_FIRST, self.baseSdds, operation, timeOverhead)
        else:
            (result, time) = self.doHeuristicApplySdds(heuristic, self.baseSdds, operation, timeOverhead)
        self.collectMostGarbage()#result) #dit toevoegen als we correctheid willen testen
        return (result, time)
        
        





    # def getNextSddToApply(self, heuristic, dataStructure = None):
    #     if heuristic == 0 or heuristic == 1 or heuristic == 4:
    #         return dataStructure.pop(0), dataStructure.pop(0), dataStructure

    #     elif heuristic == 99:
    #         firstInt = random.randint(0, len(dataStructure)-1)
    #         firstSdd = dataStructure[firstInt]
    #         secondInt = firstInt
    #         while (secondInt == firstInt):
    #             secondInt = random.randint(0, len(dataStructure)-1)
    #         secondSdd = dataStructure[secondInt]
    #         if firstInt > secondInt:
    #             dataStructure.remove(firstSdd)
    #             dataStructure.remove(secondSdd)
    #         else:
    #             dataStructure.remove(secondSdd)
    #             dataStructure.remove(firstSdd)
    #         return firstSdd, secondSdd, dataStructure
    #     else: 
    #         print("er is iets mis, heuristiek heeft geen correcte waarde / implementatie")
    #         return None, None, None

    # def updateDatastructure(self, newSdd, heuristic, datastructure):
    #     if heuristic == 0 or heuristic == 99:
    #         datastructure.append(newSdd)
    #     elif heuristic == 1 or heuristic == 4: 
    #         datastructure.update(newSdd)
    #     else: 
    #         print("er is iets mis, heuristiek heeft geen correcte waarde / implementatie")

    #class vtreeDevision():
    # left bevat een nieuwe opsplitsing
    #     right ook
    #     middle bevat de sdds die niet in left noch in right kunnen
    # def __init__(self, sdds, parentVtreeNode) -> None:
    #     if len(sdds) <= 2:
    #         self.left = None
    #         self.right = None
    #         self.middle = sdds
    #     else:
    #         self.vtreeNode = parentVtreeNode
    #         leftSdds = []
    #         rightSdds = []
    #         self.middle = []
    #         for sdd in sdds:
    #             #(leftVar, rightVar) = self.getOutsides(sdd)
    #             #in principe zou je zo iets kunnen doen, en dan met leftVar en rightVar de vtree kunnen traverseren,    
    #             #maar dat is niet nodig want er is een functie SddNode.vtree(), die de vtree node geeft waarvoor de sdd is genormalizeerd
    #             # + Vtree.left en Vtree.right om de left en right child van een bep. vtree node te krijgen 
    #             if Vtree.is_sub(sdd.vtree(), parentVtreeNode.left()):
    #                 leftSdds.append(sdd)
    #             if Vtree.is_sub(sdd.vtree(), parentVtreeNode.right()):
    #                 rightSdds.append(sdd)
    #             else: #side = middle
    #                 self.middle.append(sdd)
    #         if len(leftSdds) == 0:
    #             self.left = None
    #         elif len(leftSdds) == 1:
    #             self.left = None
    #             self.middle.append(leftSdds[0])
    #         else:
    #             self.left = self.vtreeDevision(leftSdds, self.vtreeNode.left())
    #         if len(rightSdds) == 0:
    #             self.left = None
    #         elif len(rightSdds) == 1:
    #             self.right = None
    #             self.middle.append(rightSdds[0])
    #         else:
    #             self.right = self.vtreeDevision(rightSdds, self.vtreeNode.right())

    # def getNextSddToApply(self):
    #     if self.left is None and self.right is None:
    #         ret
    #     if self.left is not None:
    #         return self.left.getNextSddsToApply()
            
                
    # in def getNextSdd...()      
    #     elif heuristic == 2:
    #         if dataStructure is None:
    #             dataStructure = self.vtreeDevision(sdds, self.compiler.sddManager.vtree())
    #         (sdd1, sdd2) = dataStructure.getNextSddsToApply()
    #         return sdd1, sdd2, dataStructure
    
    # def minimize_baseSdds_vtrees(self):
    #     for i in self.loadBaseSdds():
    #         newVtree = self.compiler.sddManager.vtree_minimize()
    #         newSddManager = SddManager.from_vtree(newVtree)
    #         newCompiler = SDDcompiler(self.nrOfVars, newSddManager)
    #     pass
        
    # def minimize_final_vtree(self):
    #     newVtree = self.compiler.sddManager.vtree().minimize(self.compiler.sddManager)
    #     self.compiler.sddManager.garbage_collect()
    #     newSddManager = SddManager.from_vtree(newVtree)
    #     self.compiler = SDDcompiler(self.nrOfVars, newSddManager)

    
    # def minimize_base_sdds(self):
    #     self.saveBaseSdds()
    #     self.compiler.sddManager.minimize()
    #     self.unsaveBaseSdds()

    # def minimize_only_final(self):
    #     finalSdd = self.doRandomApply()
    #     finalSdd.ref()
    #     self.compiler.sddManager.minimize()
    #     finalSdd.deref()

    # def minimize_with_all(self):
    #     finalSdd = self.doRandomApply()
    #     finalSdd.ref()
    #     self.saveBaseSdds()
    #     self.compiler.sddManager.minimize()
    #     finalSdd.deref()
    #     self.unsaveBaseSdds()