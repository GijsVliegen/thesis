#dot -Tpng -O sdd.dot
from randomOrderApplier import RandomOrderApply, SddVarAppearancesList, SddVtreeCountList
from randomOrderApplier import RANDOM, SMALLEST_FIRST, VTREESPLIT, VTREESPLIT_WITH_SMALLEST_FIRST, VTREE_VARIABLE_ORDERING, ELEMENT_UPPERBOUND
from randomOrderApplier import AND, OR

from pysdd.sdd import SddManager, Vtree, WmcManager, SddNode
from flatSDDCompiler import SDDcompiler
import ctypes
import os
import timeit
import graphviz
import itertools
import math


def rightAndBalancedSdd():
    balanced_vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="balanced")
    # 3:{all}
    # 1:{a,b}      5:{c,d}
    # 0:{a} 2:{b}  4:{c}    6:{d}
    balanced_mgr = SddManager.from_vtree(balanced_vtree)
    a, b, c, d = balanced_mgr.vars
    f = (a & b) | (b & c) | (c & d)
    with open(f"figs/other_figs/balanced_sdd_example", "w") as out:
        print(f.dot(), file=out)
        graphviz.Source(f.dot()).render(f"figs/other_figs/balanced_sdd_example", format='png')

    right_vtree = Vtree(var_count=4, var_order=[1, 2, 3, 4], vtree_type="right")
    # 3:{all}
    # 1:{a,b}      5:{c,d}
    # 0:{a} 2:{b}  4:{c}    6:{d}
    right_mgr = SddManager.from_vtree(right_vtree)
    a, b, c, d = right_mgr.vars
    f = (a & b) | (c & d)
    with open(f"figs/other_figs/right_linear_sdd_example", "w") as out:
        print(f.dot(), file=out)
        graphviz.Source(f.dot()).render(f"figs/other_figs/right_linear_sdd_example", format='png')

rightAndBalancedSdd()