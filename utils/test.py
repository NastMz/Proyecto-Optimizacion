from Core.Analysis import Analysis
from Core.Board import Board
from Core.Simplex import Simplex

# board = Board(
#     variables=['X1', 'X2', 'S1', 'S2', 'S3', 'A1', 'A2', 'CR'],
#     solution_variables=['A1', 'A2', 'S3'],
#     solution_coefficients=[1, 1, 0],
#     solution_phase_two_coefficients=[5, 7, 0],
#     function_coefficients=[5, 7, 0, 0, 0, 0, 0, 0],
#     restrictions_coefficients=[
#         [1, 0, -1, 0, 0, 1, 0, 100],
#         [-2, 1, 0, -1, 0, 0, 1, 0],
#         [1, 1, 0, 0, 1, 0, 0, 500]
#     ],
#     function_phase_one_coefficients=[0, 0, 0, 0, 0, 1, 1, 0]
# )

# board = Board(
#     variables=['X1', 'X2', 'X3', 'X4', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12', 'A1',
#                'A2', 'A3', 'A4', 'CR'],
#     solution_variables=['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'A1', 'A2', 'A3', 'A4'],
#     solution_coefficients=[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
#     function_coefficients=[1918, 1158, 896, 1868, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     restrictions_coefficients=[
#         [12, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 19051],
#         [0, 10, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 22680],
#         [0, 0, 50, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10000],
#         [0, 0, 0, 60, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3780],
#         [1421, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 750000],
#         [0, 858, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 325000],
#         [0, 0, 664, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 325000],
#         [0, 0, 0, 1384, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 600000],
#         [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 0, 10],
#         [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1, 0, 0, 10],
#         [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1, 0, 4],
#         [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 1, 6]
#     ],
#     function_phase_one_coefficients=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
# )
#
# boards_phase_one, boards_phase_two = Simplex().simplex_two_phases(board)
#
# interation = 0
# print('Fase 1: ')
# for board in boards_phase_one:
#     print(interation)
#     for row in board:
#         print(row)
#     interation += 1
#
# interation = 0
# print('Fase 2: ')
# for board in boards_phase_two:
#     print(interation)
#     for row in board:
#         print(row)
#     interation += 1


a = Analysis()

b = a.solution

c = a.solution.get_objective_value()

print(a.interval_coefficients[0][1])