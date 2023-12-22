from randomCNFGenerator import generateRandomCnfFormula, generateRandomCnfDimacs
from flatSDDCompiler import SDDcompiler
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
import random
import ctypes

class RandomOrderApply():

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

    def __init__(self, nrOfSdds, nrOfVars, nrOfClauses, nrOfCnfs, cnf3 = True, operation = "OR"):
        self.nrOfSdds = nrOfSdds
        self.nrOfVars = nrOfVars
        self.nrOfClauses = nrOfClauses
        self.operation = operation
        self.operationInt = 0 if self.operation == "AND" else 1
        self.cnf3 = cnf3
        """
        AND operatie -> 10 keer 50 clauses: zelfde als een cnf met 500 clauses -> skewed result?
        """ 
        self.compiler = SDDcompiler(nrOfVars=nrOfVars)
        self.baseSdds = self.generateRandomSdds(nrOfCnfs= nrOfCnfs)

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

    --------kwadratische heuristieken------------
    10 -> verwachte grootte / upper bound van de apply op 2 sdd's
    11 -> verwacht aantal vars / upper bound van de apply op 2 sdd's
    """

    def insort_right(self, sortedList, newElement, key, lo=0, hi=None):
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
        sortedList.insert(lo, newElement)

    def getNextSddToApply(self, sdds, heuristic, dataStructure = None):
        if heuristic == 0: 
            return sdds[-1], sdds[-2], None
        elif heuristic == 1:
            if dataStructure is None:
                #dataStructure = deque(sorted(childrenSdd, key=lambda sdd: sdd.size()))  #eventuele deque implementatie
                dataStructure = sorted(sdds, key=lambda sdd: sdd.size())
                return dataStructure.pop(0), dataStructure.pop(0), dataStructure
            else:
                return dataStructure.pop(0), dataStructure.pop(0), dataStructure
        elif heuristic == 99:
            firstInt = random.randint(0, len(sdds)-1)
            firstSdd = sdds[firstInt]
            secondInt = firstInt
            while (secondInt == firstInt):
                secondInt = random.randint(0, len(sdds)-1)
            secondSdd = sdds[secondInt]
            return firstSdd, secondSdd, None
        else: 
            print("er is iets mis, heuristiek heeft geen correcte waarde / implementatie")
            return None, None, None

    def updateDatastructure(self, newSdd, childrenSdd, heuristic, datastructure):
        if heuristic == 0: 
            pass
        elif heuristic == 1: 
            self.insort_right(datastructure, newSdd, key=lambda sdd: sdd.size())
        elif heuristic == 99:
            pass
        else: 
            print("er is iets mis, heuristiek heeft geen correcte waarde / implementatie")

    def doRandomApply(self):
        return self.doHeuristicApply(99)

    #kan mss nog beter gemaakt worden dmv de linker en rechter variable op te slaan samen met de sdd
    #-> snellere computatie van in welke vtree node de sdd zit (links of rechts of beide)
    def doHeuristicApply2Recursive(self, sdds, parentVtreeNode, innerHeuristic = 99):
        #recursively split up the children in left.children, right.children en middle.children
        # left children samen (recursief?) applyen, dan right.children, en dan middle.children
        if len(sdds) == 1:
            return sdds[0]
        if parentVtreeNode is None: #bijvoorbeeld omdat
            pass
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
        if len(left) == 1:
            middle.append(left[0])
        elif len(left) >= 2: 
            middle.append(self.doHeuristicApply2Recursive(left, parentVtreeNode.left(), innerHeuristic))
        if len(right) == 1:
            middle.append(right[0])
        elif len(right) >= 2: 
            middle.append(self.doHeuristicApply2Recursive(right, parentVtreeNode.right(), innerHeuristic))
        return self.doHeuristicApplySdds(middle, innerHeuristic)

    def doHeuristicApplySdds(self, sdds, heuristic = 1): #base value zou moeten veranderd worden naar de beste sdd
        datastructure = None
        while len(sdds) > 1:
            sdd1, sdd2, datastructure = self.getNextSddToApply(sdds, heuristic, datastructure)
            sdds.remove(sdd1)
            sdds.remove(sdd2)
            newSdd = self.compiler.sddManager.apply(sdd1, sdd2, self.operationInt)
            self.updateDatastructure(newSdd, sdds, heuristic, datastructure) #eerst dataStructure updaten, die gebruikt maakt van alle 
            #overige elementen in childrenSdd, pas daaarne newSdd toevoegen aan childrenSdd
            sdds.append(newSdd)
            #doSomethingWithResults(rootNodeId, rootNode, newSdd, datastructure)
        self.collectMostGarbage(sdds[0])
        return sdds[0]

    def doHeuristicApply(self, heuristic):
        sdds = self.baseSdds.copy()
        if heuristic == 2:
            return self.doHeuristicApply2Recursive(sdds, self.compiler.sddManager.vtree(), 99)
        if heuristic == 3:
            return self.doHeuristicApply2Recursive(sdds, self.compiler.sddManager.vtree(), 1)
        return self.doHeuristicApplySdds(sdds, heuristic)
        
        # if sdds[0].is_true(): #true or false trivial sdd
        #     print(f"de sdd is triviaal true, er zijn nog {len(sddsCopy)} sdds over")
        # if sdds[0].is_false(): #true or false trivial sdd
        #     print(f"de sdd is triviaal false, er zijn nog {len(sddsCopy)} sdds over")
        
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