from randomCNFGenerator import generateRandomCnf
from flatSDDCompiler import SDDcompiler
from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
import random
import ctypes

class RandomOrderApply():

    def minimize_baseSdds_vtrees(self):
        for i in self.loadBaseSdds():
            newVtree = self.compiler.sddManager.vtree_minimize()
            newSddManager = SddManager.from_vtree(newVtree)
            newCompiler = SDDcompiler(self.nrOfVars, newSddManager)
        pass
        
    def minimize_final_vtree(self):
        newVtree = self.compiler.sddManager.vtree().minimize(self.compiler.sddManager)
        self.compiler.sddManager.garbage_collect()
        newSddManager = SddManager.from_vtree(newVtree)
        self.compiler = SDDcompiler(self.nrOfVars, newSddManager)
        newBaseSdds = self.loadBaseSdds()
        self.baseSdds = newBaseSdds
        self.saveBaseSdds

    def size(self):
        return self.compiler.sddManager.size()

    def __enter__(self):
        print(f" entry dead count = {self.compiler.sddManager.dead_count()}")
        return self #needed to return object to variable after 'as'
    def __exit__(self, exc_type, exc_value, traceback):
        print(f" exit dead count = {self.compiler.sddManager.dead_count()}")
        self.compiler.SddManager.garbage_collect()

    def __init__(self, nrOfSdds, nrOfVars, nrOfClauses, cnf3 = True, operation = "OR"):
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
        self.baseSdds = []
        self.filename = f"savedSdds/baseSdds_{nrOfSdds}_{nrOfVars}_{nrOfClauses}_{cnf3}_{operation}"
        self.generateRandomSdds()
        self.saveBaseSdds()

    def collectGarbage(self):
        self.compiler.sddManager.garbage_collect()

    def generateRandomSdds(self, nrOfCnfs = 1):
        for i in range(self.nrOfSdds):
            newSdd = self.compiler.sddManager.false()
            for j in range(nrOfCnfs):
                nextCnf = generateRandomCnf(self.nrOfClauses, self.nrOfVars, self.cnf3)
                (nextSdd, _) = self.compiler.compileToSdd(nextCnf)
                newSdd = self.compiler.sddManager.apply(newSdd, nextSdd, 1)
            self.compiler.sddManager.minimize_cardinality(newSdd)
            self.baseSdds.append(newSdd)

    def saveBaseSdd(self, index):
        pass

    def saveBaseSdds(self):
        if len(self.baseSdds) == 0:
            self.generateRandomSdds()
        for i in range(self.nrOfSdds):
            baseSdd = self.baseSdds[i]
            filenameStr = self.filename + str(i)
            filenameBytes = filenameStr.encode('utf-8')
            filenamePointer = ctypes.create_string_buffer(filenameBytes)
            filenamePtrRepresentation = ctypes.cast(filenamePointer, ctypes.c_char_p).value
            baseSdd.save(filenamePtrRepresentation)

    def loadBaseSdd(self, index):
        pass

    def loadBaseSdds(self):
        baseSdds = []
        for i in range(self.nrOfSdds):
            filenameStr = self.filename + str(i)
            filenameBytes = filenameStr.encode('utf-8')
            filenamePointer = ctypes.create_string_buffer(filenameBytes)
            filenamePtrRepresentation = ctypes.cast(filenamePointer, ctypes.c_char_p).value
            baseSdds.append(self.compiler.sddManager.read_sdd_file(filenamePtrRepresentation))
        return baseSdds

    def getRandomNextSddsToApply(self, sdds):

        firstInt = random.randint(0, len(sdds)-1)
        firstSdd = sdds[firstInt]
        secondInt = firstInt
        while (secondInt == firstInt):
            secondInt = random.randint(0, len(sdds)-1)
        secondSdd = sdds[secondInt]
        return firstSdd, secondSdd

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

    def doHeuristicApply(self, sdds, heuristic):
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

    def doRandomApply(self, sdds):
        while len(sdds) > 1:
            (firstSdd, secondSdd) = self.getRandomNextSddsToApply(sdds)
            sdds.remove(firstSdd)
            sdds.remove(secondSdd)
            appliedSdd = self.compiler.sddManager.apply(firstSdd, secondSdd, self.operationInt)
            sdds.append(appliedSdd)
            #print(f"live count van alle nodes = {self.compiler.sddManager.live_count()}")
            #print(f"dead count van alle nodes = {self.compiler.sddManager.dead_count()}")
        return sdds[0]
        """if sdds[0].is_true(): #true or false trivial sdd
            print(f"de sdd is triviaal true, er zijn nog {len(sddsCopy)} sdds over")
        if sdds[0].is_false(): #true or false trivial sdd
            print(f"de sdd is triviaal false, er zijn nog {len(sddsCopy)} sdds over")"""
        
        