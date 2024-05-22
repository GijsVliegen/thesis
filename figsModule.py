#dot -Tpng -O sdd.dot
from heuristicApplier import HeuristicApply, SddVarAppearancesList, SddVtreeCountList
from heuristicApplier import RANDOM, KE, VP, VP_KE, VO, EL
from heuristicApplier import AND, OR

from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from flatSDDCompiler import SDDcompiler
import ctypes
import os
import timeit
import graphviz
import itertools
import math

def rightAndBalancedVtree():
    balanced_vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="balanced")
    graphviz.Source(balanced_vtree.dot()).render(f"figs/other_figs/balanced_vtree_example", format='svg')
    right_vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="right")
    graphviz.Source(right_vtree.dot()).render(f"figs/other_figs/right_vtree_example", format='svg')

def rightAndBalancedSdd():
    balanced_vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="balanced")
    # 3:{all}
    # 1:{a,b}      5:{c,d}
    # 0:{a} 2:{b}  4:{c}    6:{d}
    balanced_mgr = SddManager.from_vtree(balanced_vtree)
    a, b, c, d = balanced_mgr.vars
    f = (a & b) | (b & c) | (c & d)
    graphviz.Source(f.dot()).render(f"figs/other_figs/balanced_sdd_example", format='svg')
    graphviz.Source(f.dot()).render(f"figs/other_figs/balanced_sdd_example", format='png')

    right_vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="right")
    # 3:{all}
    # 1:{a,b}      5:{c,d}
    # 0:{a} 2:{b}  4:{c}    6:{d}
    right_mgr = SddManager.from_vtree(right_vtree)
    a, b, c, d = right_mgr.vars
    f = (a & b) | (c & d)
    graphviz.Source(f.dot()).render(f"figs/other_figs/right_linear_sdd_example", format='svg')
    graphviz.Source(f.dot()).render(f"figs/other_figs/right_linear_sdd_example", format='png')

# rightAndBalancedVtree()
rightAndBalancedSdd()