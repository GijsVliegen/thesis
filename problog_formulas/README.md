propositional_formula.py contains data structure to represent a logical formula with each node being either an ATOM, conjunction (CONJ) or disjunction (DISJ).
The formula is a list of such nodes. The children of a conjunction node is a tuple of indices, e.g. (4,8,10), that refers to the formula nodes nodes[4], nodes[8], and nodes[10].

The pickle files are formula instances you can experiment with. A Bayesian network [source](https://www.bnlearn.com/bnrepository/discrete-medium.html#alarm) was converted into a ProbLog program (alarm.pl). A pickled instance is created by adding a query and running `problog_to_lf.py`.

`analyze_formula.py` shows how to read in such a pickled instance, and prints the content of the formula. You should be able to analyze them without needing problog itself.


