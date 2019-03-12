# "MVP"
# Use by calling the function with the math question to be solved in quotes, eg:
# python VeryBadSolution.py "1 + 2 * 5 / (3-1)"
#
# WARNING: Very much a bad solution. Never ever to be used.


if __name__ == "__main__":
    import sys

    print(eval(sys.argv[1]))
