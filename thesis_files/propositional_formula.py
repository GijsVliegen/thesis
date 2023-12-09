import itertools
import operator
from collections.abc import Collection

from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum


class FormulaOp(Enum):
    """ Possible formula operations """
    CONJ = 1
    DISJ = 2
    ATOM = 3
    NEG = 4


@dataclass(frozen=True)
class RefFormula(object):
    """
        A formula whose subformulas (children) are represented by referencing their index
        in a FormulaContainer that stores this formula.

        Assumptions:
            * for all children: child >= 0
            * If op == FormulaOp.ATOM then len(children) == 0
            * If op == FormulaOp.NEG then len(children) == 1
    """
    # __slots__ = ["op", "children"]  # problems with loading pickle files.

    op: FormulaOp
    children: Tuple[int, ...]


class FormulaContainer:
    """
        A container of Acyclic formulas

        Each formula is of type RefFormula.
    """

    def __init__(self):
        # Do not remove formulas, because other formulas might refer to those.
        self._formulas: List[RefFormula] = []
        self._nb_vars: int = 0

    def get_nb_vars(self) -> int:
        """ Get the number of atoms (variables) in this container """
        return self._nb_vars

    def add_formula(self, formula: RefFormula) -> int:
        """ Add a formula to this container, returns a reference to the formula. """
        assert (formula.op == FormulaOp.ATOM or len(formula.children) > 0)
        assert (  # validate formula -- DAG check
            all((1 <= x <= len(self._formulas)) for x in formula.children)
        )
        self._formulas.append(formula)
        if formula.op == FormulaOp.ATOM:
            self._nb_vars += 1
        return len(self._formulas)

    def get_formula(self, formula_id: int) -> RefFormula:
        """ get the formula stored on the given formula reference """
        assert formula_id >= 1
        return self._formulas[formula_id-1]

    def __iter__(self):
        """ Iterate over all formulas """
        return self._formulas.__iter__()

    def __len__(self) -> int:
        return len(self._formulas)