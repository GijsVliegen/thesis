from randomCNFGenerator import generateRandomCnfFormula
from flatSDDCompiler import SDDcompiler
from pysdd.sdd import Vtree, SddManager, SddNode
import random
import time
import os

#CONSTANTS
KE = 1                  #kleinste eerst
VP = 2                  #Vtree partitionering
VP_KE = 3               #Vtree partitionering + Kleinste eerst
VO = 4                  #variabelen volgorde
EL = 5                  #element_count
IVO_LR = 6              #inverse variabelen volgorde left to right
IVO_RL = 7              #inverse variabelen volgorde right to left
VP_EL = 8               #Vtree partitionering + element_count
ELVAR = 9               #probeersel
VP_ELVAR = 10           #probeersel 2
IVO_RL_EL = 11          #combinatie heuristiek op basis van variabelen in sdd
IVO_RL_EL_Size = 12     #combo heuristiek op basis van grootte van sdd
RANDOM = 99             #random compilatie

OR = 1
AND = 0

heuristicDict = {RANDOM: "Random", KE: "KE", VP: "VP", 
                 EL: "EL", VP_KE: "VP + KE", 
                 VO: "TD", IVO_LR: "BU-LR",
                 IVO_RL: "BU-RL", VP_EL:"VP + EL", ELVAR:"EL-Var", VP_ELVAR:"VP + EL-Var",
                 IVO_RL_EL: "BU-EL", IVO_RL_EL_Size: "BU-EL-Size"}

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
    #returns sdd at index
    def pop(self, index):
        return super().pop(index)
    
    #adds sdd to the datastructure
    def update(self, newSdd): #gebruikt in eigen code
        self.append(newSdd)

    #returns 2 sdds from the datastructure to apply
    def getNextSddsToApply(self):
        return self.pop(0), self.pop(0)
    
    def __getitem__(self, index):
        return super().__getitem__(index)
    def _insert(self, index, newSddSize): #inserts object thats already of right type
        super().insert(index, newSddSize)

#datastructure voor random heuristiek: kiest telkens 2 random sdds uit een list 
class RandomList(ExtendedList):
    def __init__(self, sdds, randomizerSeed):
        super().__init__(sdds)
        # print(random.randint(0, 100))
        # self.randomizer = random.Random(randomizerSeed)
    def getNextSddsToApply(self):
        firstInt = random.randint(0, len(self)-1)
        firstSdd = self[firstInt]
        self.remove(firstSdd)
        secondInt = random.randint(0, len(self)-1)
        secondSdd = self[secondInt]
        self.remove(secondSdd)
        return firstSdd, secondSdd

#datastructure voor Kleinste eerst
#houdt een lijst bij van SddSize (achter de schermen), die gesorteerd zijn per size van de sdd 
class SddSizeList(ExtendedList):
    def __init__(self, sdds):
        super().__init__(sdds)
    # def pop(self, index): //als niet werkt, dit gewoon uncommenten, evetnueel spelen met getSdd()
    #     return super().pop(index) 
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
    

#datastructure voor probeersel
#houdt een lijst bij van tupels (sizeEstimate, SddVarCount a, SddVarCount b) (achter de schermen)
# -> kiest telkens de twee sdds met een lage upperbound (5.1.2 en 5.1.3), zonder de upperbound van local_vtree_element_count(5.1.1)
class SddVarCountList(ExtendedList):
    def __init__(self, sdds, sddManager):
        super().__init__([]) #roept append op voor elke sdd in 
        self.sizeEstimateTuples = ExtendedList([])
        self.vtreeRoot = sddManager.vtree()
        self.sddManager = sddManager
        for i in sdds:
            self.append(i)
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
    #     sdd = super().pop(index)
    # def insert(self, index, newSdd):      #onnuttige en onlogische functie voor deze structuur
    #     super.insert(index, self.SddVtreeCount(newSdd))
    def append(self, newSdd):
        varList = self.sddManager.sdd_variables(newSdd)
        newSddVarCount = self.SddVarCount(newSdd, varList)
        for sddVarCount in self:
            newSizeEstimateTuple = (SddVarCountList._getUpperLimit(sddVarCount, newSddVarCount, self.vtreeRoot), sddVarCount, newSddVarCount)
            insort_right(self.sizeEstimateTuples, newSizeEstimateTuple, key=lambda x: x[0])
        super().append(newSddVarCount)

    #upperbound na apply van 2 sdds volgens 5.1.2 en 5.1.3
    def _getUpperLimit(sddVarCount1, sddVarCount2, root):
        combinedVars = [int(x or y) for x,y in zip(sddVarCount1.varList, sddVarCount2.varList)]
        varsPerVtreeNode = SddVarCountList.varsUnderVtreeNode(combinedVars, root)
        combinedVarCount = SddVarCountList.upperbound(varsPerVtreeNode, root)
            
        return sum(combinedVarCount)
    
    #returned een lijst met als:
    #    index: stelt vtreeknoop voor
    #    element: upperbound van nodes onder die vtreeknoop volgens 5.1.2 en 5.1.3 in thesis
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

    #returned een lijst met als:
    #    index: stelt vtreeknoop voor
    #    element: aantal aanwezige variabelen onder die vtreeknoop 
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
            self.topVtreeNode = sdd.vtree()
            self.varList = varList
        
        def getSdd(self):
            return self.sdd



#datastructure voor Element_count
#houdt een lijst bij van tupels (sizeEstimate, SddVtreeCount a, SddVtreeCount b) (achter de schermen)
# -> kiest telkens de twee sdds met een lage upperbound, zonder de upperbound van local_vtree_element_count
class SddVtreeCountList(ExtendedList):
    def __init__(self, sdds, sddManager):
        super().__init__([]) #roept append op voor elke sdd in 
        self.sizeEstimateTuples = ExtendedList([])
        self.vtreeRoot = sddManager.vtree()
        self.sddManager = sddManager
        for i in sdds:
            self.append(i)
    # def pop(self, index): //als niet werkt, dit gewoon uncommenten
    #     return super().pop(index)
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
    #     sdd = super().pop(index)
    # def insert(self, index, newSdd):      #onnuttige en onlogische functie voor deze structuur
    #     super.insert(index, self.SddVtreeCount(newSdd))
    def append(self, newSdd):
        varList = self.sddManager.sdd_variables(newSdd)
        newSddVtreeCount = self.SddVtreeCount(newSdd, varList)
        for sddVtreeCount in self:
            newSizeEstimateTuple = (SddVtreeCountList._getUpperLimit(sddVtreeCount, newSddVtreeCount, self.vtreeRoot), sddVtreeCount, newSddVtreeCount)
            insort_right(self.sizeEstimateTuples, newSizeEstimateTuple, key=lambda x: x[0])
        super().append(newSddVtreeCount)

    #berekend upperbound size na apply van twee sdds volgens thesissectie 5.1.1, 5.1.2 en 5.1.3
    def _getUpperLimit(sddVtreeCount1, sddVtreeCount2, root):
        root1 = sddVtreeCount1.topVtreeNode
        root2 = sddVtreeCount2.topVtreeNode
        if (root1 is None):
            return sum(sddVtreeCount2.vtreeCount)
        if (root2 is None):
            return sum(sddVtreeCount1.vtreeCount)
        
        #overloopt de vtreenode om te kijken over ergens een extra factor in rekening gebracht moet worden
        #zie sectie 5.1.4
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
        
        #vermenigvuldiging van aantal elementen per vtreeknoop
        newVtreeCount = []
        for (i,j) in zip(tempVtreeCount1, tempVtreeCount2):
            if i == 0 and j != 0: i = 1
            if i != 0 and j == 0: j = 1
            newVtreeCount.append(i*j)
        
        #extra upperbound toepassen volgens 5.1.2/5.1.3
        combinedVars = [int(x or y) for x,y in zip(sddVtreeCount1.varList, sddVtreeCount2.varList)]
        varsPerVtreeNode = SddVtreeCountList.varsUnderVtreeNode(combinedVars, root)
        newVtreeCount = SddVtreeCountList.extraUpperbound(newVtreeCount, varsPerVtreeNode, root)
            
        return sum(newVtreeCount)
    
    #past extra upperbound uit 5.1.2 en 5.1.3 toe op voorlopige upperbound

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

    #returned een lijst met als:
    #    index: stelt vtreeknoop voor
    #    element: aantal aanwezige variabelen onder die vtreeknoop 
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
            self.vtreeCount = sdd.local_vtree_element_count()
            self.topVtreeNode = sdd.vtree()
            self.varList = varList
        
        def getSdd(self):
            return self.sdd
        
        #zie thesis sectie 5.1.4: 
        #   local_vtree_element_count niet altijd volledig als sdds niet genormaliseerd zijn voor zelfde vtreeknoop
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
#varpriority is standaard Top-Down en Links naar Rechts
#   inverse = True  -> bottom-up
#   LR = False      -> Rechts naar Links
class SddVarAppearancesList(ExtendedList):
    def __init__(self, sdds, sddManager, inverse = False, LR = True):
        self.var_order = SddVarAppearancesList.getVarPriority(sddManager.vtree(), LR)
        if (inverse):
            self.var_order.reverse()
        self.sddManager = sddManager
        super().__init__(sdds)
    
    def pop(self, index): #als niet werkt, dit gewoon uncommenten
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
            varList = mgr.sdd_variables(sdd)
            #self.varsUsed is de cumulatieve som van aanwezige variabelen volgens de var_order:
            #   aanwezige vars = a b c, voorgesteld als [1, 1, 1, 0, 0]
            #   var_order = d b e a c, voorgesteld als [4, 2, 5, 1, 3]
            #   -> varsUsed = [2, 1, 3, 0, 1] (staat dus in volgorde a b c d e)
            #   -> varsUsed in var_order volgorde = [0, 1, 1, 2, 3] (voor extra duidelijkheid)
            self.varsUsed = list(map(lambda i_el_tuple: sum(varList[1:i_el_tuple[0]+2]), enumerate(varList[1:])))#sum van elke subarray

        #ordering op sdds volgens de aanwezige variabelen
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

#datatstuctuur voor combo heuristiek op basis van groottes:
    #intern een datastructuur voor 
    #   heuristiek Element_count: als sdd.size > threshold
    #   heuristiek Inverse Var Order RL als sdd.size < threshold
    #kiest eerst sdds uit Inverse Var Order RL, daarna de rest 
class combinedHeuristicListSize(ExtendedList):
    def __init__(self, sdds, sddManager, nrOfVariables, threshold):
        self.ratio = threshold
        # print(self.ratio)
        self.nrOfVars = nrOfVariables
        self.mgr = sddManager
        variabelenvolgordeLijst = []
        upperboundLijst = []
        for sdd in sdds:
            if sdd.size() < self.ratio:
                variabelenvolgordeLijst.append(sdd)
            else:
                upperboundLijst.append(sdd)
        #Element count datastructuur
        self.upperBoundHeur = SddVtreeCountList(upperboundLijst, self.mgr)
        #Inverse Var Order RL datastructuur
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
    
    #zolang er "kleine" sdds zijn die kiezen om te applyen
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

#datatstuctuur voor combo heuristiek op basis van aantal variabelen:
    #intern een datastructuur voor 
    #   heuristiek Element_count: als sdd.size > ratio * nrOfVars
    #   heuristiek Inverse Var Order RL als sdd.size < ratio * nrOfVars
    #kiest eerst sdds uit Inverse Var Order RL, daarna de rest 
class combinedHeuristicList(ExtendedList):
    def __init__(self, sdds, sddManager, nrOfVariables, threshold):
        self.ratio = threshold
        # print(self.ratio)
        self.nrOfVars = nrOfVariables
        self.mgr = sddManager
        variabelenvolgordeLijst = []
        upperboundLijst = []
        for sdd in sdds:
            if sum(self.mgr.sdd_variables(sdd)) < self.ratio*self.nrOfVars:
                variabelenvolgordeLijst.append(sdd)
            else:
                upperboundLijst.append(sdd)
        #Element count datastructuur
        self.upperBoundHeur = SddVtreeCountList(upperboundLijst, self.mgr)
        #Inverse Var Order RL datastructuur
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
        if sum(self.mgr.sdd_variables(newSdd)) < self.ratio*self.nrOfVars and len(self.varOrderHeur) > 0:
            self.varOrderHeur.update(newSdd)
        else:
            self.upperBoundHeur.update(newSdd)
        if len(self.varOrderHeur) == 1:
            sdd = self.varOrderHeur.pop(0)
            self.upperBoundHeur.update(sdd)

    def update(self, newSdd): #insert new element while keeping sortedness
        self.append(newSdd)

    
#wordt gebruikt voor bepaalde list structuren
"""Insert item x in list a, and keep it sorted assuming a is sorted.
    If x is already in a, insert it to the right of the rightmost x.
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
def insort_right(sortedList, newElement, key = lambda x: x, lo=0, hi=None):
    

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

    #generates new base sdds
    def renew(self):
        self.sddManager.garbage_collect()
        self.baseSdds = self.generateRandomSdds(self.operation)

    def size(self):
        return self.sddManager.size()
    
    #garbage collect except base sdds and parameter
    def collectMostGarbage(self, sdd = None):
        self.saveBaseSdds()
        if sdd is not None: sdd.ref()
        self.sddManager.garbage_collect()
        if sdd is not None: sdd.deref()
        self.unsaveBaseSdds()

    def collectAllGarbage(self):
        self.sddManager.garbage_collect()

    # def __enter__(self):
    #     print(f" entry dead count = {self.sddManager.dead_count()}")
    #     return self #needed to return object to variable after 'as'
    # def __exit__(self, exc_type, exc_value, traceback):
    #     print(f" exit dead count = {self.sddManager.dead_count()}")
    #     self.sddManager.garbage_collect()

    #restarts the applier with a new vtree
    def setVtree(self, vtree):
        self.sddManager = SddManager.from_vtree(vtree)
        self.baseSdds = self.generateRandomSdds(self.operation)
        self.collectMostGarbage()

    #initialisatie van het applyen van nrOfSdds sdds
        #-nrOfSdds = aantal baseSdds (CNFs) dat wordt gegeneerd om te applyen
        #-nrOfVars = aantal variabelen waarmee elke CNF zal gegeneerd worden
        #-nrOfClauses = aantal clauses waarmee elke CNF zal gegeneerd worden 
        #-operation = conjunctie of disjunctie
        #-randomSeed wordt gebruikt voor de random Heuristiek verschillend te laten werken tussen verschillende computing nodes
        #-als vtree_type = random moet er een vtree meegegeven worden 
        #   (ivm reproductie van experimenten + zelfde random vtree op meerdere computing nodes)
        #-threshold is de threshold gebruikt voor de Combo heuristieken
    def __init__(self, nrOfSdds, nrOfVars, nrOfClauses, operation, randomSeed, vtree_type = "balanced", vtree = -1, threshold = 0.70):
        # random.seed(randomSeed)
        self.nrOfSdds = nrOfSdds
        self.nrOfVars = nrOfVars
        self.nrOfClauses = nrOfClauses
        self.operation = operation
        self.cnf3 = True
        if vtree_type == "random":
            self.sddManager = SddManager.from_vtree(vtree)
        else:
            vtree = Vtree(var_count=nrOfVars, vtree_type=vtree_type)
            self.sddManager = SddManager.from_vtree(vtree)
        self.compilerForCNFs = SDDcompiler(nrOfVars=nrOfVars, sddManager=self.sddManager)
        self.baseSdds = self.generateRandomSdds(operation)
        self.threshold = threshold

    def generateRandomSdds(self, operation):
        randomSdds = []
        for _ in range(self.nrOfSdds):
            cnf = generateRandomCnfFormula(self.nrOfClauses, self.nrOfVars, self.cnf3)
            sdd = self.compilerForCNFs.compileToSdd(cnf, len(cnf), self.sddManager)
            #convert into dnf
            if operation == AND:
                sdd = self.sddManager.negate(sdd)
            randomSdds.append(sdd)
        return randomSdds

    def saveBaseSdds(self):
        for baseSdd in self.baseSdds:
            baseSdd.ref()       
            
    def unsaveBaseSdds(self):
        for baseSdd in self.baseSdds:
            baseSdd.deref()
    
    def doApply(self, sdd1, sdd2):
        newSdd = self.sddManager.apply(sdd1, sdd2, self.operation)
        return newSdd

    # initialisation of datastructure for heuristic, measures time
    def getFirstDataStructure(self, sdds, heuristic, seed = -1):
        startTime = time.time()
        if heuristic == KE:
            res = SddSizeList(sdds)
        if heuristic == VO:
            res = SddVarAppearancesList(sdds, self.sddManager)
        if heuristic == IVO_LR:
            res = SddVarAppearancesList(sdds, self.sddManager, inverse=True, LR=True)
        if heuristic == IVO_RL:
            res = SddVarAppearancesList(sdds, self.sddManager, inverse=True, LR=False)
        if heuristic == EL:
            res = SddVtreeCountList(sdds, self.sddManager)
        if heuristic == RANDOM:
            if seed != -1:
                print(f"seed given = {seed}")
                res = RandomList(sdds, seed)
            else: 
                res = RandomList(sdds, sdds[0].size())#*sdds[1].size())
        if heuristic == ELVAR:
            res = SddVarCountList(sdds, self.sddManager)
        if heuristic == IVO_RL_EL_Size:
            res = combinedHeuristicListSize(sdds, self.sddManager, self.nrOfVars, self.threshold)
        if heuristic == IVO_RL_EL:
            res = combinedHeuristicList(sdds, self.sddManager, self.nrOfVars, self.threshold)
        return (res, time.time() - startTime)
        #else: print(f"heuristiek {heuristic} is nog niet geïmpleneteerd")

    #function to apply sdds using Vtree Partitioning
    #   -innerHeuristic is tweede interne gebruikte heuristiek
    #   -timeOverhead is een ongebruikte boolean
    #returned [finalSdd, intermediateSizes, intermediateNrOfVars, /, totalTime, time without overhead
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
                    [sum(self.sddManager.sdd_variables(newSdd))], \
                        [-1], timed, timed)
        if parentVtreeNode is None:
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
        #recursief links
        if len(left) > 0:
            (recursiveSdd, recurSizeList, recurVarCounts, recurDepthList, recursiveTime, recurNoOHtime) = self.doHeuristicApply2Recursive\
                (parentVtreeNode.left(), innerHeuristic, left, timeOverhead)
            middle.append(recursiveSdd)
            sizeList += recurSizeList
            varCounts += recurVarCounts
            depthList += recurDepthList
            totalTime += recursiveTime
            noOverheadTime += recurNoOHtime
        #recursief rechts
        if len(right) > 0:
            (recursiveSdd, recurSizeList, recurVarCounts, recurDepthList, recursiveTime, recurNoOHtime) = self.doHeuristicApply2Recursive\
                (parentVtreeNode.right(), innerHeuristic, right, timeOverhead)
            middle.append(recursiveSdd)
            sizeList += recurSizeList
            varCounts += recurVarCounts
            depthList += recurDepthList
            totalTime += recursiveTime
            noOverheadTime += recurNoOHtime
        #de rest volgens tweede interne heuristiek
        (resultSdd, extraSizes, extraVarCounts, extraDepthList, extraTime, extraNoOHtime) = self.doHeuristicApplySdds\
            (innerHeuristic, middle, timeOverhead)
        return (resultSdd, sizeList + extraSizes, varCounts + extraVarCounts, \
                depthList + extraDepthList, totalTime + extraTime, noOverheadTime + extraNoOHtime)

    #function to apply sdds according to a heuristic
    #   -timeOverhead is een ongebruikte boolean
    #returned [finalSdd, intermediateSizes, intermediateNrOfVars, /, totalTime, time without overhead
    def doHeuristicApplySdds(self, heuristic, sdds, timeOverhead, seed = -1): 
        noOverheadTime = 0
        compileSizes = []
        varCounts = []
        depthList = []

        #elementaire gevallen
        if len(sdds) == 2:  
            startTime = time.time()
            finalSdd = self.doApply(sdds[0], sdds[1])
            extraTime = time.time() - startTime
            compileSizes.append(finalSdd.size())
            varCounts.append(sum(self.sddManager.sdd_variables(finalSdd)))
            depthList.append(-1)
            return (finalSdd, compileSizes, varCounts, depthList, extraTime, extraTime)
        if len(sdds) == 1:
            finalSdd = sdds[0]
            compileSizes.append(finalSdd.size())
            varCounts.append(sum(self.sddManager.sdd_variables(finalSdd)))
            depthList.append(-1)
            return (finalSdd, compileSizes, varCounts, depthList, 0, 0)
        
        #initialisatie van datastructuur
        (datastructure, totalTime)  = self.getFirstDataStructure(sdds, heuristic)
        if seed != -1:
            (datastructure, totalTime)  = self.getFirstDataStructure(sdds, heuristic, seed = seed)
        
        #applyen van sdds tot een finaal resultaat
        while len(datastructure) > 2:
            overheadStartTime = time.time()
            sdd1, sdd2 = datastructure.getNextSddsToApply()
            startTime = time.time()
            newSdd = self.doApply(sdd1, sdd2)
            noOverheadTime += time.time() - startTime
            datastructure.update(newSdd)
            totalTime += time.time() - overheadStartTime

            compileSizes.append(newSdd.size())
            varCounts.append(sum(self.sddManager.sdd_variables(newSdd)))
            depthList.append(-1)
            #doSomethingWithResults(rootNodeId, rootNode, newSdd, datastructure)

        if len(datastructure) == 2:  #datastructuur hoeft niet meer gebruikt te worden
            overheadStartTime = time.time()
            sdd1, sdd2 = datastructure.getNextSddsToApply()
            startTime = time.time()
            finalSdd = self.doApply(sdd1, sdd2)
            noOverheadTime += time.time() - startTime
            totalTime += time.time() - overheadStartTime

            compileSizes.append(finalSdd.size())
            varCounts.append(sum(self.sddManager.sdd_variables(finalSdd)))
            depthList.append(-1)
            return (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime)
        else:
            return (sdds[0], compileSizes, varCounts, depthList, totalTime, noOverheadTime)
    
    #function to run one experiment for a heuristic
    #returns:
    #   -finalSdd
    #   -compileSizes:  list of sizes of the intermediate results
    #   -varCoutns:     list of nr of vars in each intermediate result
    #   -depthList:     probeersel, functionaliteit is weg
    #   -totalTime:     totale compilatieTijd
    #   -noOverheadTime:compilatietijd zonder overhead van gebruik heuristiek (datastructuur etc.)
    def doHeuristicApply(self, heuristic, timeOverhead = True, seed = -1):
        #print(f"using heuristic {heuristic}")
        if heuristic == VP:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.sddManager.vtree(), RANDOM, self.baseSdds, timeOverhead)
        elif heuristic == VP_KE:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.sddManager.vtree(), KE, self.baseSdds, timeOverhead)
        elif heuristic == VP_EL:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.sddManager.vtree(), EL, self.baseSdds, timeOverhead)
        elif heuristic == VP_ELVAR:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.sddManager.vtree(), ELVAR, self.baseSdds, timeOverhead)
        elif heuristic == IVO_RL_EL:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.sddManager.vtree(), IVO_RL_EL, self.baseSdds, timeOverhead)
        elif heuristic == IVO_RL_EL_Size:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApply2Recursive\
                (self.sddManager.vtree(), IVO_RL_EL_Size, self.baseSdds, timeOverhead)
        else:
            (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime) = self.doHeuristicApplySdds(heuristic, self.baseSdds, timeOverhead, seed = seed)
        # self.collectMostGarbage(finalSdd) #dit toevoegen als we correctheid willen testen -> correctheid testen door sizes te vergelijken?
        return (finalSdd, compileSizes, varCounts, depthList, totalTime, noOverheadTime)

    #function to run one experiment for a heuristic with CNF's of different sizes (zie thesissectie 6.7)
    #returns:
    #   -finalSdd
    #   -compileSizes:  list of sizes of the intermediate results
    #   -varCoutns:     list of nr of vars in each intermediate result
    #   -depthList:     probeersel, functionaliteit is weg
    #   -totalTime:     totale compilatieTijd
    #   -noOverheadTime:compilatietijd zonder overhead van gebruik heuristiek (datastructuur etc.)
    def randomRatiosApply(self, heuristic, renew = True, seed = -1):
        if renew:
            randomSdds = []
            for _ in range(self.nrOfSdds):
                nrOfClauses = random.randint(1, 4.5*self.nrOfVars) #wordt geseed tijdens init
                cnf = generateRandomCnfFormula(nrOfClauses, self.nrOfVars, self.cnf3)
                (sdd, _) = self.compilerForCNFs.compileToSdd(cnf, len(cnf))
                #convert into dnf
                if self.operation == AND:
                    sdd = self.sddManager.negate(sdd)
                # sddWrapper = SDDwrapper(sdd, depth = 0)
                # randomSdds.append(sddWrapper)
                randomSdds.append(sdd)
            self.baseSdds = randomSdds
        
        return self.doHeuristicApply(heuristic, seed = seed)

    #initialises the Applier with custom sdds to apply
    def setManuelApply(self, sdds, nrOfVars, operation, sddManager):
        self.nrOfSdds = len(sdds)
        self.nrOfVars = nrOfVars
        self.sddManager = sddManager
        self.baseSdds = []
        for sdd in sdds:
            self.baseSdds.append(sdd)
        self.operation = operation

    def getBaseApplier():
        return HeuristicApply(0, 3, 0, 0, -1)

#apply a number of sdds according to a heuristic
#returns:
#   -finalSdd
#   -compileSizes:  list of sizes of the intermediate results
#   -varCoutns:     list of nr of vars in each intermediate result
#   -depthList:     probeersel, functionaliteit is weg
#   -totalTime:     totale compilatieTijd
#   -noOverheadTime:compilatietijd zonder overhead van gebruik heuristiek (datastructuur etc.)
#NrOfVars, operation & sddManager moeten vooraf geinitialiseerd worden voor functionaliteit
def heuristicApplyCustom(sdds, nrOfVars, operation, heuristic, sddManager):
    heuristicApplier = HeuristicApply.getBaseApplier()
    heuristicApplier.setManuelApply(sdds, nrOfVars, operation, sddManager)
    return heuristicApplier.doHeuristicApply(heuristic)


