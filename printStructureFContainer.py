import pickle

from thesis_files.propositional_formula import FormulaContainer


def load_formula_from_pickle(filename: str) -> FormulaContainer:
    with open(filename, "rb") as f:
        formula = pickle.load(f)
    return formula


def main(filename: str):
    formula = load_formula_from_pickle(filename)
    print(f"Number of variables: {formula.get_nb_vars()}")
    for index, node in enumerate(formula):
        print(f"node {index+1} =\t{node}")


if __name__ == "__main__":
    main(filename="thesis_files/alarm_pRESS_zero.pickle")      # 89 vars, 207 nodes
    # main(filename="./alarm_bP_low.pickle")        # 582 vars, 1228 nodes
    # main(filename="./alarm_sAO2_normal.pickle")   # 305 vars, 641 nodes
    # main(filename="./alarm_vENTALV_high.pickle")  # 197 vars, 416 nodes
