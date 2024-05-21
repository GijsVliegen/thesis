def chancheVarNotInClausule(vars, k):
    return (vars-k)/vars

def chancheVarNotInCNF(vars, k, ratio):
    return chancheVarNotInClausule(vars, k) ** (ratio * vars)

def chancheVarInCNF(vars, k, ratio):
    return 1 -chancheVarNotInCNF(vars, k ,ratio)

def chancheAllVarInCnf(vars, k, ratio):
    return chancheVarInCNF(vars,k , ratio) ** vars

vars = 28
k = 3
ratios = list(range(1, 20))
for i in ratios:
    ratio = i/4
    print(f"ratio = {ratio}: {chancheVarInCNF(vars, k, ratio)}")