import glob
import pickle
import os
from typing import Optional, Dict

from problog.formula import LogicDAG
from problog.program import PrologFile
from problog.logic import Term
from problog.engine import DefaultEngine

from logic_formulas.propositional_formula import FormulaContainer, FormulaOp, RefFormula


class ProbLogToFContainerCompiler:
    """
    Convert a LogicDAG (ProbLog class) to a FormulaContainer.
    A FormulaContainer uses the same representation but strips away irrelevant code/attributes.
    """

    def __init__(self):
        self.container: FormulaContainer = FormulaContainer()
        self.cid_to_fid: Dict[int, int] = dict()  # child id to formula id

    def compile(self, lf: LogicDAG) -> FormulaContainer:
        """
        Convert a LogicDAG (ProbLog class) to a FormulaContainer.
        A FormulaContainer uses the same representation but strips away irrelevant code/attributes.

        :param lf: A logical formula
        :type lf: LogicDAG
        :return: A formula container representing the logical formula lf
        :rtype: FormulaContainer
        """
        self.container = FormulaContainer()
        self.cid_to_fid = dict()
        for i, n, t in lf:
            if t == "atom":
                self._add_atom(i)
            else:
                self._add_apply(i, n, t)
        result = self.container
        # reset vars
        self.container = FormulaContainer()
        self.cid_to_fid = dict()
        return result

    def _add_atom(self, cid: int):
        f = RefFormula(FormulaOp.ATOM, tuple())
        fid = self.container.add_formula(f)
        self.cid_to_fid[cid] = fid
        return fid

    def _add_apply(self, cid: int, node, node_t: str):
        assert node_t == "conj" or node_t == "disj"
        operation = FormulaOp.CONJ if node_t == "conj" else FormulaOp.DISJ

        def _child_map(x):
            # if child does not exist yet, it must be a negation.
            _fid = self.cid_to_fid.get(x)
            if _fid is None:
                assert x < 0
                _fid = self._add_neg(x, self.cid_to_fid[abs(x)])
            return _fid
        f = RefFormula(operation, tuple(_child_map(child) for child in node.children))
        fid = self.container.add_formula(f)
        self.cid_to_fid[cid] = fid
        return fid

    def _add_neg(self, cid: int, child_fid: int):
        f = RefFormula(FormulaOp.NEG, tuple([child_fid]))
        neg_fid = self.container.add_formula(f)
        self.cid_to_fid[cid] = neg_fid
        return neg_fid


def problog_to_fcontainer(lf: LogicDAG) -> FormulaContainer:
    """
    Convert a LogicDAG (ProbLog class) to a FormulaContainer.
    A FormulaContainer uses the same representation but strips away irrelevant code/attributes.

    :param lf: A logical formula
    :type lf: LogicDAG
    :return: A formula container representing the logical formula lf
    :rtype: FormulaContainer
    """
    return ProbLogToFContainerCompiler().compile(lf)


def filename_to_fcontainer(filename) -> FormulaContainer:
    model = PrologFile(filename)
    engine = DefaultEngine(label_all=True)
    db = engine.prepare(model)
    queries = engine.query(db, Term("query", None))
    # print("Queries:", ", ".join([str(q[0]) for q in queries]))
    evidence = engine.query(db, Term("evidence", None, None))
    # print("Evidence:", ", ".join(["%s=%s" % ev for ev in evidence]))
    gp = engine.ground_all(db)
    gp = LogicDAG.createFrom(gp)
    print(f"LogicDAG size: {len(gp)}")
    container = problog_to_fcontainer(gp)
    return container


def main(filename: str, output: Optional[str] = None):
    # setup input + output
    filename_is_dir = os.path.isdir(filename)
    assert filename_is_dir or os.path.isfile(filename), f"filename {filename} must be an existing file or directory."

    if filename_is_dir:
        filepaths = glob.glob(filename + '/**/*.pl', recursive=True)
        filepaths = [os.path.abspath(p) for p in filepaths]
        assert output is None or os.path.isdir(output), f"output {output} must be a directory, similar to the input."
        if output is None:
            output = filename
    else:
        filepaths = [os.path.abspath(filename)]
        assert output is None or os.path.isfile(output), f"output {output} must be a file, similar to the input."
        if output is None:
            name, extension = os.path.splitext(filename)
            output = name + ".pickle"

    # perform actual work
    for fpath in filepaths:
        print(f"-- Converting {os.path.basename(fpath)} --")
        container = filename_to_fcontainer(filename=fpath)

        # store where?
        if filename_is_dir:
            relative_path = os.path.relpath(fpath, filename)  # e.g. ./benchmarks/problog minus ./benchmarks/
            relative_path_noext, extension = os.path.splitext(relative_path)
            outputpath = os.path.join(output, relative_path_noext)
            foutput = outputpath + ".pickle"
        else:
            foutput = output
        # print(foutput)

        with open(foutput, "wb") as f:
            pickle.dump(container, f)


if __name__ == "__main__":
    main(
        filename="./alarm.pl",
    )
# if __name__ == "__main__":
#     import argparse
#
#     argparser = argparse.ArgumentParser()
#     argparser.add_argument("filename", type=str,
#                            help="A path to a ProbLog filename or directory containing .pl problog files.")
#     argparser.add_argument("-o", "--output", type=str,
#                            default=None,
#                            help="A path to the output file. When filename is a directory, then this must be too.")
#     args = argparser.parse_args()
#
#     main(**vars(args))
