from randomCNFGenerator import generateRandomCnfFormula
from flatSDDCompiler import SDDcompiler
from pysdd.sdd import Vtree
import random
import time
import os

KE = 1
VP = 2
VP_KE = 3
VO = 4
EL = 5
IVO_LR = 6
IVO_RL = 7
VP_EL = 8
ELVAR = 9
VP_ELVAR = 10
IVO_RL_EL = 11
IVO_RL_EL_Size = 12
RANDOM = 99
OR = 1
AND = 0
heuristicDict = {RANDOM: "Random", KE: "KE", VP: "VP", 
                 EL: "EL", VP_KE: "VP + KE", 
                 VO: "TD", IVO_LR: "BU-LR",
                 IVO_RL: "BU-RL", VP_EL:"VP + EL", ELVAR:"EL-Var", VP_ELVAR:"VP + EL-Var",
                 IVO_RL_EL: "BU-EL", IVO_RL_EL_Size: "BU-EL-Size"}


class SDDwrapper:
    def __init__(self, sdd, depth):
        self.sdd = sdd
        self.depth = depth
    def size(self):
        return self.sdd.size()
    def vtree(self):
        return self.sdd.vtree()
    def getSdd(self):
        return self.sdd
    def local_vtree_element_count(self):
        return self.sdd.local_vtree_element_count()
    def getDepth(self):
        return self.depth
    def ref(self):
        self.sdd.ref()
    def deref(self):
        self.sdd.deref()

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
    def __init__(self, sdds, randomizerSeed):
        super().__init__(sdds)
        self.randomizer = random.Random(randomizerSeed)
    def getNextSddsToApply(self):
        firstInt = self.randomizer.randint(0, len(self)-1)
        firstSdd = self[firstInt]
        self.remove(firstSdd)
        secondInt = self.randomizer.randint(0, len(self)-1)
        secondSdd = self[secondInt]
        self.remove(secondSdd)
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
    
class SddVarCountList(ExtendedList):
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
        (_, sddVarCount1, sddVarCount2) = self.sizeEstimateTuples.pop(0)
        index = 0
        while index < len(self.sizeEstimateTuples):
            sizeEstimateTuple = self.sizeEstimateTuples[index]
            if (sddVarCount1 == sizeEstimateTuple[1] or sddVarCount1 == sizeEstimateTuple[2] or 
                sddVarCount2 == sizeEstimateTuple[1] or sddVarCount2 == sizeEstimateTuple[2]):
                del self.sizeEstimateTuples[index]
            else:
                index += 1
        self.remove(sddVarCount1)
        self.remove(sddVarCount2)
        return sddVarCount1.getSdd(), sddVarCount2.getSdd()
    # def pop(self, index):                 #onnuttig en onlgische functie voor deze structuur
    #     sdd = super().pop(index).getSdd()
    # def insert(self, index, newSdd):      #onnuttige en onlogische functie voor deze structuur
    #     super.insert(index, self.SddVtreeCount(newSdd))
    def append(self, newSdd):
        varList = self.sddManager.sdd_variables(newSdd.getSdd())
        newSddVarCount = self.SddVarCount(newSdd, varList)
        for sddVarCount in self:
            newSizeEstimateTuple = (SddVarCountList._getUpperLimit(sddVarCount, newSddVarCount, self.vtreeRoot), sddVarCount, newSddVarCount)
            #newSizeEstimateTuple = (5, sddVtreeCount, newSddVtreeCount)
            #om een of andere reden werkt dit niet -> brute force insert
            insort_right(self.sizeEstimateTuples, newSizeEstimateTuple, key=lambda x: x[0])
        super().append(newSddVarCount)

    def _getUpperLimit(sddVarCount1, sddVarCount2, root):
        root1 = sddVarCount1.topVtreeNode
        root2 = sddVarCount2.topVtreeNode
        # if (root1 is None):
        #     return sum(sddVarCount2.vtreeCount)
        # if (root2 is None):
        #     return sum(sddVarCount1.vtreeCount)
        #root = Vtree.lca(root1, root2, root)
        combinedVars = [int(x or y) for x,y in zip(sddVarCount1.varList, sddVarCount2.varList)]
        varsPerVtreeNode = SddVarCountList.varsUnderVtreeNode(combinedVars, root)
        combinedVarCount = SddVarCountList.upperbound(varsPerVtreeNode, root)
            
        return sum(combinedVarCount)
    
    def upperbound(varsPerVtreeNode, root):
        queue = [root]
        varCount = varsPerVtreeNode.copy()
        while len(queue) > 0: #veel simpelere implementatie die de volledige vtree overloopt
            currentNode = queue.pop(0)
            parentElCount = 1
            if (not currentNode.is_leaf()): #geen rootnode -> nog hoger level
                queue.append(currentNode.left())
                queue.append(currentNode.right())
                varLimit = 2**(min(varsPerVtreeNode[currentNode.left().position()], 2**varsPerVtreeNode[currentNode.right().position()]))
                varCount[currentNode.position()] = parentElCount*varLimit
            else:
                varCount[currentNode.position()] = 1
        return varCount

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
        leftList = SddVarCountList.varsUnderVtreeNode(varList, vtreeNode.left(), left, vtreeNode.position())
        rightList = SddVarCountList.varsUnderVtreeNode(varList, vtreeNode.right(), vtreeNode.position() + 1, right)
        return leftList + [sum(varList[int(left/2): int((right+1)/2)])] + rightList
        
    class SddVarCount:
        def __init__(self, sdd, varList):
            self.sdd = sdd
            #self.vtreeCount = [0, 2, 0, 2, 0, 4, 4, 2, 4, 2, 0, 2, 4, 2] #zeker lang genoeg zodat er geen out of bounds access gebeurt
            self.topVtreeNode = sdd.vtree()
            self.varList = varList
        
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
        varList = self.sddManager.sdd_variables(newSdd.getSdd())
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
        self.var_order = SddVarAppearancesList.getVarPriority(sddManager.vtree(), LR)
        if (inverse):
            self.var_order.reverse()
        self.sddManager = sddManager
        super().__init__(sdds)
    
    def pop(self, index):
        return super().pop(index).getSdd()
    def insert(self, index, newSdd):
        newSddVarAppearance = self.SddVarAppearance(newSdd, self.var_order, self.sddManager)
        super().insert(index, newSddVarAppearance)
    def append(self, newSdd):
        insort_right(self, self.SddVarAppearance(newSdd, self.var_order, self.sddManager))
    def update(self, newSdd): #insert new element while keeping sortedness
        self.append(newSdd)

    class SddVarAppearance:
        def __init__(self, sdd, var_order, mgr):
            self.sdd = sdd
            self.var_order = var_order
            varList = mgr.sdd_variables(sdd.getSdd())
            self.varsUsed = list(map(lambda i_el_tuple: sum(varList[1:i_el_tuple[0]+2]), enumerate(varList[1:])))#sum van elke subarray
        def __lt__(self, other):
            if self.varsUsed[0] == 0: 
                return True
            if other.varsUsed[0] == 0:
                return False
            for i in self.var_order:
                if self.varsUsed[i-1] == self.varsUsed[-1]: #geen andere vars meer -> ook goed
                    return True
                if other.varsUsed[i-1] == other.varsUsed[-1]:
                    return False
                if self.varsUsed[i-1] > other.varsUsed[i-1]: #als die een voorkomen heeft van een variabele hoog en links in de vtree en other niet -> sdd eerst zetten
                    return True
                if self.varsUsed[i-1] < other.varsUsed[i-1]:
                    return False
            return False
        def getSdd(self):
            return self.sdd
    
    #LR geeft aan of de vtree van links naar rechts of van rechts naar links moet doorlopen worden
    def getVarPriority(vtree, LR):
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

#work in progress
#ivo_RL is het beste en VP_EL
class combinedHeuristicListSize(ExtendedList):
    def __init__(self, sdds, sddManager, nrOfVariables, threshold):
        self.ratio = threshold
        print(self.ratio)
        self.nrOfVars = nrOfVariables
        self.mgr = sddManager
        variabelenvolgordeLijst = []
        upperboundLijst = []
        for sdd in sdds:
            if sdd.size() < self.ratio:
                variabelenvolgordeLijst.append(sdd)
            else:
                upperboundLijst.append(sdd)
        self.upperBoundHeur = SddVtreeCountList(upperboundLijst, self.mgr)
        self.varOrderHeur = SddVarAppearancesList(variabelenvolgordeLijst, self.mgr, inverse = True, LR = False)
    
    def __len__(self):
        return len(self.upperBoundHeur) + len(self.varOrderHeur)
    
    def pop(self, index):
        #wordt enkel gebruikt om het laatste element te poppen
        if (index > 0):
            print(f"error , index > 0: index = {index}")
        if len(self.varOrderHeur) > 0:
            return self.varOrderHeur.pop(index)
        else: return self.upperBoundHeur.pop(index)
    
    def getNextSddsToApply(self):
        if len(self.varOrderHeur) >= 2:
            return self.varOrderHeur.getNextSddsToApply()
        else:
            return self.upperBoundHeur.getNextSddsToApply()

    def append(self, newSdd):
        if newSdd.size() < self.ratio and len(self.varOrderHeur) > 0:
            self.varOrderHeur.update(newSdd)
        else:
            self.upperBoundHeur.update(newSdd)
        if len(self.varOrderHeur) == 1:
            sdd = self.varOrderHeur.pop(0)
            self.upperBoundHeur.update(sdd)

    def update(self, newSdd): #insert new element while keeping sortedness
        self.append(newSdd)

class combinedHeuristicList(ExtendedList):
    def __init__(self, sdds, sddManager, nrOfVariables, threshold):
        self.ratio = threshold
        print(self.ratio)
        self.nrOfVars = nrOfVariables
        self.mgr = sddManager
        variabelenvolgordeLijst = []
        upperboundLijst = []
        for sdd in sdds:
            if sum(self.mgr.sdd_variables(sdd.getSdd())) < self.ratio*self.nrOfVars:
                variabelenvolgordeLijst.append(sdd)
            else:
                upperboundLijst.append(sdd)
        self.upperBoundHeur = SddVtreeCountList(upperboundLijst, self.mgr)
        self.varOrderHeur = SddVarAppearancesList(variabelenvolgordeLijst, self.mgr, inverse = True, LR = False)
    
    def __len__(self):
        return len(self.upperBoundHeur) + len(self.varOrderHeur)
    
    def pop(self, index):
        #wordt enkel gebruikt om het laatste element te poppen
        if (index > 0):
            print(f"error , index > 0: index = {index}")
        if len(self.varOrderHeur) > 0:
            return self.varOrderHeur.pop(index)
        else: return self.upperBoundHeur.pop(index)
    
    def getNextSddsToApply(self):
        if len(self.varOrderHeur) == 1:
            sdd = self.varOrderHeur.pop(0)
            self.upperBoundHeur.update(sdd)
        if len(self.varOrderHeur) >= 2:
            return self.varOrderHeur.getNextSddsToApply()
        else:
            return self.upperBoundHeur.getNextSddsToApply()

    def append(self, newSdd):
        if sum(self.mgr.sdd_variables(newSdd.getSdd())) < self.ratio*self.nrOfVars and len(self.varOrderHeur) > 0:
            self.varOrderHeur.update(newSdd)
        else:
            self.upperBoundHeur.update(newSdd)
        if len(self.varOrderHeur) == 1:
            sdd = self.varOrderHeur.pop(0)
            self.upperBoundHeur.update(sdd)

    def update(self, newSdd): #insert new element while keeping sortedness
        self.append(newSdd)

    
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

class HeuristicApply():

    def extractCounts(self):
        temp = self.nodeCounterList
        self.nodeCounterList = []
        return temp

    def renew(self):
        self.compiler.sddManager.garbage_collect()
        self.baseSdds = self.generateRandomSdds(self.operation)

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

    def setVtree(self, vtree):
        self.compiler.changeVtree(vtree)
        self.baseSdds = self.generateRandomSdds(self.operation)
        self.collectMostGarbage()

    def __init__(self, nrOfSdds, nrOfVars, nrOfClauses, operation, randomSeed, vtree_type = "balanced", vtree = -1, threshold = 0.75):
        random.seed(randomSeed)
        self.nrOfSdds = nrOfSdds
        self.nrOfVars = nrOfVars
        self.nrOfClauses = nrOfClauses
        self.operation = operation
        self.cnf3 = True
        """
        AND operatie -> 10 keer 50 clauses: zelfde als een cnf met 500 clauses -> skewed result?
        """ 
        self.compiler = SDDcompiler(nrOfVars=nrOfVars, vtree_type=vtree_type)
        if vtree_type == "random":
            self.compiler.changeVtree(vtree)
        self.baseSdds = self.generateRandomSdds(operation)
        self.collectMostGarbage()
        self.nodeCounterList = []
        self.threshold = threshold

    def generateRandomSdds(self, operation):
        randomSdds = []
        for _ in range(self.nrOfSdds):
            cnf = generateRandomCnfFormula(self.nrOfClauses, self.nrOfVars, self.cnf3)
            (sdd, size) = self.compiler.compileToSdd(cnf, len(cnf))
            #convert into dnf
            if operation == AND:
                sdd = self.compiler.sddManager.negate(sdd)
            sddWrapper = SDDwrapper(sdd, depth = 0)
            randomSdds.append(sddWrapper)
        return randomSdds

    def saveBaseSdds(self):
        for baseSdd in self.baseSdds:
            baseSdd.ref()       
            
    def unsaveBaseSdds(self):
        for baseSdd in self.baseSdds:
            baseSdd.deref()
    
    def doApply(self, sdd1, sdd2):
        newDepth = max(sdd1.getDepth(), sdd2.getDepth()) + 1
        newSdd = self.compiler.sddManager.apply(sdd1.getSdd(), sdd2.getSdd(), self.operation)
        newSddwrapper = SDDwrapper(newSdd, newDepth)
        return newSddwrapper

    # SMALLEST_FIRST = 1
    # VTREESPLIT = 2
    # VTREESPLIT_WITH_SMALLEST_FIRST = 3
    # VTREE_VARIABLE_ORDERING = 4
    # ELEMENT_UPPERBOUND = 5
    # INVERSE_VAR_ORDER_LR = 6
    # INVERSE_VAR_ORDER_RL = 7
    # VTREESPLIT_WITH_EL_UPPERBOUND = 8
    # RANDOM = 99
    def getFirstDataStructure(self, sdds, heuristic, seed = -1):
        startTime = time.time()
        if heuristic == KE:
            res = SddSizeList(sdds)
        if heuristic == VO:
            res = SddVarAppearancesList(sdds, self.compiler.sddManager)
        if heuristic == IVO_LR:
            res = SddVarAppearancesList(sdds, self.compiler.sddManager, inverse=True, LR=True)
        if heuristic == IVO_RL:
            res = SddVarAppearancesList(sdds, self.compiler.sddManager, inverse=True, LR=False)
        if heuristic == EL:
            res = SddVtreeCountList(sdds, self.compiler.sddManager)
        if heuristic == RANDOM:
            if seed != -1:
                print(f"seed given = {seed}")
                res = RandomList(sdds, seed)
            else: 
                res = RandomList(sdds, sdds[0].size()*sdds[1].size())
        if heuristic == ELVAR:
            res = SddVarCountList(sdds, self.compiler.sddManager)
        if heuristic == IVO_RL_EL_Size:
            res = combinedHeuristicListSize(sdds, self.compiler.sddManager, self.nrOfVars, self.threshold)
        if heuristic == IVO_RL_EL:
            res = combinedHeuristicList(sdds, self.compiler.sddManager, self.nrOfVars, self.threshold)
        return (res, time.time() - startTime)
        #else: print(f"heuristiek {heuristic} is nog niet geïmpleneteerd")

    def doHeuristicApply2Recursive(self, parentVtreeNode, innerHeuristic, sdds, timeOverhead):
        #recursively split up the children in left.children, right.children en middle.children
        # left children samen (recursief) applyen, dan right.children (recursief), en dan middle.children
        if len(sdds) == 1:
            return (sdds[0], [], [], [], 0, 0)
        if len(sdds) == 2:
            startTime = time.time()
            newSdd = self.doApply(sdds[0], sdds[1])
            timed = time.time() - startTime
            return (newSdd, [newSdd.size()], \
                    [sum(self.compiler.sddManager.sdd_variables(newSdd.getSdd()))], \
                        [newSdd.getDepth()], timed, timed)
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
        sizeList = []
        varCounts = []
        depthList = []
        totalTime = 0
        noOverheadTime = 0
        if len(left) > 0:
            (recursiveSdd, recurSizeList, recurVarCounts, recurDepthList, recursiveTime, recurNoOHtime) = self.doHeuristicApply2Recursive\
                (parentVtreeNode.left(), innerHeuristic, left, timeOverhead)
            middle.append(recursiveSdd)
            sizeList += recurSizeList
            varCounts += recurVarCounts
            depthList += recurDepthList
            totalTime += recursiveTime
            noOverheadTime += recurNoOHtime
        if len(right) > 0:
            (recursiveSdd, recurSizeList, recurVarCounts, recurDepthList, recursiveTime, recurNoOHtime) = self.doHeuristicApply2Recursive\
                (parentVtreeNode.right(), innerHeuristic, right, timeOverhead)
            middle.append(recursiveSdd)
            sizeList += recurSizeList
            varCounts += recurVarCounts
            depthList += recurDepthList
            totalTime += recursiveTime
            noOverheadTime += recurNoOHtime
        (resultSdd, extraSizes, extraVarCounts, extraDepthList, extraTime, extraNoOHtime) = self.doHeuristicApplySdds\
            (innerHeuristic, middle, timeOverhead)
        return (resultSdd, sizeList + extraSizes, varCounts + extraVarCounts, \
                depthList + extraDepthList, totalTime + extraTime, noOverheadTime + extraNoOHtime)

    def doHeuristicApplySdds(self, heuristic, sdds, timeOverhead, seed = -1): #base value zou moeten veranderd worden naar de beste heuristiek
        #print(f"nu: using heuristic {heuristic}")
        noOverheadTime = 0
        (datastructure, totalTime)  = self.getFirstDataStructure(sdds, heuristic)
        if seed != -1:
            (datastructure, totalTime)  = self.getFirstDataStructure(sdds, heuristic, seed = seed)
        compileSizes = []
        varCounts = []
        depthList = []

        while len(datastructure) > 1:
            overheadStartTime = time.time()
            sdd1, sdd2 = datastructure.getNextSddsToApply()
            startTime = time.time()
            newSdd = self.doApply(sdd1, sdd2)
            noOverheadTime += time.time() - startTime
            datastructure.update(newSdd)
            totalTime += time.time() - overheadStartTime

            compileSizes.append(newSdd.size())
            varCounts.append(sum(self.compiler.sddManager.sdd_variables(newSdd.getSdd())))
            depthList.append(newSdd.getDepth())
            #self.nodeCounterList.append(self.compiler.sddManager.dead_size())
            # self.nodeCounterList.append((self.compiler.sddManager.count(), self.compiler.sddManager.live_count(), self.compiler.sddManager.dead_count())) #count, dead_count of live_count
            #doSomethingWithResults(rootNodeId, rootNode, newSdd, datastructure)
        finalSdd = datastructure.pop(0)
        return (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime)

    def doHeuristicApply(self, heuristic, timeOverhead = True, seed = -1):
        #print(f"using heuristic {heuristic}")
        if heuristic == VP:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.compiler.sddManager.vtree(), RANDOM, self.baseSdds, timeOverhead)
        elif heuristic == VP_KE:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.compiler.sddManager.vtree(), KE, self.baseSdds, timeOverhead)
        elif heuristic == VP_EL:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.compiler.sddManager.vtree(), EL, self.baseSdds, timeOverhead)
        elif heuristic == VP_ELVAR:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.compiler.sddManager.vtree(), ELVAR, self.baseSdds, timeOverhead)
        elif heuristic == IVO_RL_EL:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.compiler.sddManager.vtree(), IVO_RL_EL, self.baseSdds, timeOverhead)
        elif heuristic == IVO_RL_EL_Size:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.compiler.sddManager.vtree(), IVO_RL_EL_Size, self.baseSdds, timeOverhead)
        else:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApplySdds(heuristic, self.baseSdds, timeOverhead, seed = seed)
        self.collectMostGarbage(finalSdd) #dit toevoegen als we correctheid willen testen -> correctheid testen door sizes te vergelijken?
        return (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime)

    def randomRatiosApply(self, heuristic, renew = True, seed = -1):
        if renew:
            randomSdds = []
            for _ in range(self.nrOfSdds):
                nrOfClauses = random.randint(1, 4.5*self.nrOfVars) #wordt geseed tijdens init
                cnf = generateRandomCnfFormula(nrOfClauses, self.nrOfVars, self.cnf3)
                (sdd, _) = self.compiler.compileToSdd(cnf, len(cnf))
                #convert into dnf
                if self.operation == AND:
                    sdd = self.compiler.sddManager.negate(sdd)
                sddWrapper = SDDwrapper(sdd, depth = 0)
                randomSdds.append(sddWrapper)
            self.baseSdds = randomSdds
        
        return self.doHeuristicApply(heuristic, seed = seed)

