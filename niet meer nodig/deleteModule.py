import os

# Specify the path to the file you want to delete
file_path = 'path/to/your/file.txt'

# Delete the file
def removeFile(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass
    except PermissionError:
        print(f"Permission denied: '{file_path}'")
    except Exception as e:
        print(f"Error deleting file '{file_path}': {e}")

def deleteAllOutputOfExperiment(vars, heuristics):
    if True:
        vtrees = ["balanced", "left", "right", "random"]
        metrics = ["sizes", "depth", "varCounts", "heuristic"]
        for vtree in vtrees:
            for metric in metrics:
                for heur in heuristics:
                    for clausules in range (int(vars/2), vars*5, int(vars/2)):
                        file_pathAnd = f"output/{metric}/test_20_{vars}_AND_{vtree}_{[heur]}_{clausules}.txt"
                        file_pathOr = f"output/{metric}/test_20_{vars}_OR_{vtree}_{[heur]}_{clausules}.txt"
                        removeFile(file_pathAnd)
                        removeFile(file_pathOr)
                        file_pathAnd = f"output/{metric}/noOverhead_20_{vars}_AND_{vtree}_{[heur]}_{clausules}.txt"
                        file_pathOr = f"output/{metric}/noOverhead_20_{vars}_OR_{vtree}_{[heur]}_{clausules}.txt"
                        removeFile(file_pathAnd)
                        removeFile(file_pathOr)

deleteAllOutputOfExperiment(12, [99, 3, 4, 5, 6, 7, 8, 9, 10])