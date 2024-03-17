from randomCNFGenerator import generateRandomCnfFormula, generateRandomCnfDimacs
from flatSDDCompiler import SDDcompiler
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode, SddManager
import random
import ctypes

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
    def update(self, newSdd):
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

class SddVtreeCountList(ExtendedList):
    def __init__(self, sdds, topvtreeNode):
        super().__init__(sdds)
        # self.vtreeOrder = self._getVtreeOrder(topvtreeNode)
        self.topvtreeNode = topvtreeNode
    def pop(self, index):
        return super().pop(index).getSdd()
    def insert(self, index, newSdd):
        super.insert(index, self.SddVtreeCount(newSdd))
    def append(self, newSdd):
        super.append(self.SddVtreeCount(newSdd))
    def update(self, newSdd):
        pass #nog in te vullen

    def getUpperLimit(self, sdd1, sdd2, topvtreeNode):
        SddVtreeCount1 = self.SddVtreeCount(sdd1)
        SddVtreeCount2 = self.SddVtreeCount(sdd2)
        return SddVtreeCount1._getUpperLimi(SddVtreeCount1, SddVtreeCount2)

    class SddVtreeCount:
        def __init__(self, sdd):
            self.sdd = sdd
            self.vtreeCount = sdd.local_vtree_element_count()
        #nog aan te vullen
        def _getUpperLimit(self, sddVtreeCount1, sddVtreeCount2):
            sdd1 = sddVtreeCount1.sdd
            sdd2 = sddVtreeCount2.sdd
            #vtree moet top-down doorlopen worden? maar hoe list juist doorlopen dan?
            topVtreeNode1 = sdd1.vtree().position()
            topVtreeNode2 = sdd2.vtree().position()
            topVtreeNode = Vtree.lca(topVtreeNode1, topVtreeNode2)
            #mbv dit de vtreeCount uitbreiden naar hogere vtree nodes indien primes
            if (topVtreeNode1 != topVtreeNode):
                currentTopNode = topVtreeNode1
                while (currentTopNode.parent() != topVtreeNode):
                    if (currentTopNode.parent().left() == currentTopNode):
                        sddVtreeCount1[currentTopNode.parent().position()] = 2
                    currentTopNode = currentTopNode.parent() 
            newVtreeCount = []
            for (i,j) in zip(sddVtreeCount1.vtreeCount, sddVtreeCount2.vtreeCount):
                if i == 0 and j != 0: i = 1
                if i != 0 and j == 0: j = 1
                newVtreeCount.append(i*j)
            newVtreeCount = self._enforceVarLimit(newVtreeCount, topVtreeNode)
            return sum(newVtreeCount)
        
        def _enforceVarLimit(self, newVtreeCount, topVtreeNode):
            return newVtreeCount

        # def _sumListAccordingToVtree(self, vtreeCount, vtreeOrder, index):
        #     levelCount = vtreeCount[index]
        #     (left, right) = vtreeOrder[index]
        #     if left != -1: levelCount += vtreeCount[index] * self._sumListAccordingToVtree(vtreeCount, vtreeOrder, left)
        #     if right != -1: levelCount += vtreeCount[index] * self._sumListAccordingToVtree(vtreeCount, vtreeOrder, right)
        #     return levelCount

    def _getVtreeOrder(topVtreeNode):
        vtreeOrdering = {}
        queue = [topVtreeNode.root()]
        while len(queue) > 0:
            nextVtreeNode = queue.pop(0)
            if nextVtreeNode.is_leaf() == 1:
                vtreeOrdering[nextVtreeNode.position()] = (-1, -1)
            if nextVtreeNode.is_leaf() == 0:
                leftVtree = nextVtreeNode.left()
                rightVtree = nextVtreeNode.right()
                queue.append(leftVtree)
                queue.append(rightVtree)
                vtreeOrdering[nextVtreeNode.position()] = (leftVtree.position(), rightVtree.position())
        return vtreeOrdering


#houdt een lijst bij van SddVarAppearance (achter de schermen), die gesorteerd zijn volgens de varpriority
class SddVarAppearancesList(ExtendedList):
    def __init__(self, sdds, sddManager):
        self.var_order = self.getVarPriority(sddManager.vtree())
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
    def update(self, newSdd):
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
        
    def getVarPriority(self, vtree):
        varOrdering = []
        queue = [vtree]
        while len(queue) > 0:
            nextVtreeNode = queue.pop(0)
            if nextVtreeNode.is_leaf() == 1:
                varOrdering.append(nextVtreeNode.var())
            else:
                leftVtree = nextVtreeNode.left()
                rightVtree = nextVtreeNode.right()
                queue.append(leftVtree)
                queue.append(rightVtree)
        return varOrdering
        #breadth first de vtree doorlopen, en dan de varOrder opslaan
        
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

    def __init__(self, nrOfSdds, nrOfVars, nrOfClauses, nrOfCnfs = 1, cnf3 = True, operation = "OR", vtree_type = "balanced"):
        self.nrOfSdds = nrOfSdds
        self.nrOfVars = nrOfVars
        self.nrOfClauses = nrOfClauses
        self.operation = operation
        self.operationInt = 0 if self.operation == "AND" else 1
        self.cnf3 = cnf3
        """
        AND operatie -> 10 keer 50 clauses: zelfde als een cnf met 500 clauses -> skewed result?
        """ 
        self.compiler = SDDcompiler(nrOfVars=nrOfVars, vtree_type=vtree_type)
        self.baseSdds = self.generateRandomSdds(nrOfCnfs= nrOfCnfs)
        self.nodeCounterList = []

    def generateRandomSdds(self, nrOfCnfs = 1):
        randomSdds = []
        for i in range(self.nrOfSdds):
            newSdd = self.compiler.sddManager.false()
            for j in range(nrOfCnfs): #maakt het mogelijk om elke baseSdd uit meerdere cnfs te laten bestaan

                nextCnf = generateRandomCnfFormula(self.nrOfClauses, self.nrOfVars, self.cnf3)
                (nextSdd, _) = self.compiler.compileToSdd(nextCnf)

                #nextCnf = generateRandomCnfDimacs(self.nrOfClauses, self.nrOfVars, self.cnf3)
                #maakt een nextSdd aan met als default vtree = 'balanced'
                #(newSddManager, nextSdd) = self.compiler.sddManager.from_cnf_string(nextCnf)#
                #nextSdd.copy(self.compiler.sddManager)

                newSdd = self.compiler.sddManager.apply(newSdd, nextSdd, 1)
            randomSdds.append(newSdd)
        return randomSdds

    def saveBaseSdds(self):
        for baseSdd in self.baseSdds:
            baseSdd.ref()       
            
    def unsaveBaseSdds(self):
        for baseSdd in self.baseSdds:
            baseSdd.deref()

    """bevat de heuristiek implementatie

    kiest de volgende twee sdd's uit een lijst, die daarna geapplied moeten worden
    ook tussenresultaten worden hier geregistreerd

    goeie vraag of een heuristiek eventueel operationInt kan/moet gebruiken voor zijn werking

    voor heuristieken de zich baseren op de ene sdd zelf, gebruik sorted list en maintain die, element toevoegen = O(log n)
    -> complexiteit O(n*log(n)), met n = aantal kinderen

    voor heuristieken die de combinatie van twee sdd's gebruikt, is een cache object nodig (lijst of dict ofzo), die de heuristiekwaarde voor dat paar bijhoudt
    -> met cache, O(n^2); zonder cache, O(n^3), met n = aantal kinderen

    mogelijke heuristieken zijn:
    0 -> default
    99 -> random volgorde
    --------lineare heuristieken--------------
    1 -> grootte van sdd
        DataStructure = sorted list
            -> O(1) om te deleten vooraan
            -> O(log(n)) om te inserten
        of DataStructure = sorted list
            -> O(n) om te deleten vooraan, maar puur op het aantal keer adressen
            -> O(log(n)) om te inserten
    2 -> sdds recursief opsplitsen in 3 subsets left, right en middle adhv vtree, en dan overblijvende sdds met innerHeuristiek 99
    3 -> 2 maar dan met innerHeuristiek 1
    4 -> van elke sdd oplijsten welke variabelen een voorkomen hebben, dan mbv. die lijst een volgorde opstellen,
        waarbij een voorkomen van een variabele hoog in de vtree (ondiep) en links, geprioriteerd wordt
        -> heuristiek 4 is zeer goed bij laag aantal clauses/vars verhouding 

    --------kwadratische heuristieken------------
    10 -> verwachte grootte / upper bound van de apply op 2 sdd's
    11 -> verwacht aantal vars / upper bound van de apply op 2 sdd's
    """

    def getFirstDataStructure(self, sdds, heuristic):
        if heuristic == 1 or heuristic == 4:
            #return deque(sorted(childrenSdd, key=lambda sdd: sdd.size()))  #eventuele deque implementatie
            if heuristic == 1:
                dataStructure = SddSizeList(sdds)
            else: #heuristic == 4
                dataStructure = SddVarAppearancesList(sdds, self.compiler.sddManager)
            dataStructure.sort()
            return dataStructure
        elif heuristic == 0:
            return ExtendedList(sdds)
        elif heuristic == 99:
            return RandomList(sdds)
        else: print(f"heuristiek {heuristic} is nog niet geïmpleneteerd")

    def doRandomApply(self):
        return self.doHeuristicApply(99)

    #kan mss nog beter gemaakt worden dmv de linker en rechter variable op te slaan samen met de sdd
    #-> snellere computatie van in welke vtree node de sdd zit (links of rechts of beide)
    def doHeuristicApply2Recursive(self, parentVtreeNode, innerHeuristic = 99, sdds = None):
        #recursively split up the children in left.children, right.children en middle.children
        # left children samen (recursief?) applyen, dan right.children, en dan middle.children
        if sdds == None:
            sdds = self.baseSdds
        if len(sdds) == 1:
            return sdds[0]
        if parentVtreeNode is None: #bijvoorbeeld omdat
            print("iets geks met parentVtreeNode, is None...")
        left = []
        right = []
        middle = []
        for sdd in sdds:
            #(leftVar, rightVar) = self.getOutsides(sdd)
            #in principe zou je zo iets kunnen doen, en dan met leftVar en rightVar de vtree kunnen traverseren,    
            #maar dat is niet nodig want er is een functie SddNode.vtree(), die de vtree node geeft waarvoor de sdd is genormalizeerd
            # + Vtree.left en Vtree.right om de left en right child van een bep. vtree node te krijgen 
            if Vtree.is_sub(sdd.vtree(), parentVtreeNode.left()):
                left.append(sdd)
            if Vtree.is_sub(sdd.vtree(), parentVtreeNode.right()):
                right.append(sdd)
            else: #side = middle
                middle.append(sdd)
        if len(left) != 0:
            middle.append(self.doHeuristicApply2Recursive(parentVtreeNode.left(), innerHeuristic, sdds = left))
        if len(right) != 0:
            middle.append(self.doHeuristicApply2Recursive(parentVtreeNode.right(), innerHeuristic, sdds = right))
        return self.doHeuristicApplySdds(innerHeuristic, sdds = middle)

    def doHeuristicApplySdds(self, heuristic = 1, sdds = None): #base value zou moeten veranderd worden naar de beste heuristiek
        #print(f"nu: using heuristic {heuristic}")
        if sdds == None:
            sdds = self.baseSdds
        datastructure = self.getFirstDataStructure(sdds, heuristic)
        while len(datastructure) > 1:
            sdd1, sdd2 = datastructure.getNextSddsToApply()
            newSdd = self.compiler.sddManager.apply(sdd1, sdd2, self.operationInt)
            datastructure.update(newSdd)
            self.nodeCounterList.append(self.compiler.sddManager.dead_size())
            # self.nodeCounterList.append((self.compiler.sddManager.count(), self.compiler.sddManager.live_count(), self.compiler.sddManager.dead_count())) #count, dead_count of live_count
            #doSomethingWithResults(rootNodeId, rootNode, newSdd, datastructure)
        finalSdd = datastructure.pop(0)
        self.collectMostGarbage(finalSdd)
        return finalSdd

    def doHeuristicApply(self, heuristic):
        #print(f"using heuristic {heuristic}")
        if heuristic == 2:
            return self.doHeuristicApply2Recursive(self.compiler.sddManager.vtree(), 99)
        if heuristic == 3:
            return self.doHeuristicApply2Recursive(self.compiler.sddManager.vtree(), 4)
        return self.doHeuristicApplySdds(heuristic)
        
        





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