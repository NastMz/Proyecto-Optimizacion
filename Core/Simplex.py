import copy


def get_quotients(board, pivot_column):
    quotients = []
    actual_board = copy.deepcopy(board)
    actual_board.pop()
    actual_board.pop()
    for row in actual_board:
        if row[pivot_column] < 0 or row[pivot_column] > 0:
            quotients.append(row[-1] / row[pivot_column])
        else:
            quotients.append(None)
    return quotients


def get_operators(actual_board, pivot_column, pivot_row):
    operators = []
    for i in range(0, len(actual_board)):
        if i != pivot_row:
            if actual_board[i][pivot_column] > 0 or actual_board[i][pivot_column]:
                operators.append(-actual_board[i][pivot_column])
            else:
                operators.append(None)
        else:
            operators.append(None)
    return operators


def get_minor_quotient(quotients):
    minor_quotient = float('inf')
    for quotient in quotients:
        if quotient is not None and 0 <= quotient < minor_quotient:
            minor_quotient = quotient
    return minor_quotient


def get_optimality_criterion(board, function_coefficients, matrix):
    optimality_criterion = []
    for i in range(len(board.variables) - 1):
        optimality_criterion.append(function_coefficients[i] - matrix[-1][i])
    optimality_criterion.append(' ')
    return optimality_criterion


def get_zj(board, actual_board, solution_coefficients):
    zj = []
    for i in range(len(board.variables)):
        z = 0
        for j in range(len(board.restrictions_coefficients)):
            z += solution_coefficients[j] * actual_board[j][i]
        zj.append(z)

    return zj


def get_full_board(function_coefficients, variables, actual_board, solution_variables, phase_one_coefficients):
    full_board = [
        [' ', 'Cj', function_coefficients, ' '],
        [' ', 'VB', variables],
    ]
    for i in range(len(actual_board)):
        full_board.append([
            phase_one_coefficients[i],
            solution_variables[i],
            actual_board[i]
        ])
    return full_board


def get_pivot_column(board, phase):
    actual_board = copy.deepcopy(board)
    actual_board[-1].pop()
    if phase == 1:
        return actual_board[-1].index(min(actual_board[-1]))
    else:
        return actual_board[-1].index(max(actual_board[-1]))


def end_status(z, phase):
    status = True
    if phase == 1:
        for item in z:
            if item != 0:
                status = False
                break
    elif phase == 2:
        for item in z:
            if item < 0:
                status = False
                break
    return status


def solve_phase_one_of_simplex_two_phases(board):
    boards = []
    actual_board = copy.deepcopy(board.restrictions_coefficients)
    solution_variables = copy.deepcopy(board.solution_variables)
    solution_variables.append('Zj')
    solution_variables.append('Cj-Zj')
    solution_coefficients = copy.deepcopy(board.solution_coefficients)
    solution_coefficients.append(' ')
    solution_coefficients.append(' ')
    phase_two_start_board = None
    end = False
    it = 0
    while not end:
        actual_board.append(get_zj(board, actual_board, solution_coefficients))
        actual_board.append(get_optimality_criterion(board, board.function_phase_one_coefficients, actual_board))
        pivot_column = get_pivot_column(actual_board, 1)
        quotients = get_quotients(board=actual_board, pivot_column=pivot_column)

        minor_quotient = get_minor_quotient(quotients=quotients)

        pivot_row = quotients.index(minor_quotient)
        pivot_element = actual_board[pivot_row][pivot_column]

        boards.append(copy.deepcopy(
            get_full_board(board.function_phase_one_coefficients, board.variables, actual_board, solution_variables,
                           solution_coefficients)))

        solution_variables[pivot_row] = board.variables[pivot_column]
        solution_coefficients[pivot_row] = board.function_phase_one_coefficients[pivot_column]
        end = end_status(actual_board[-2], 1)
        actual_board.pop()
        actual_board.pop()

        if end:
            phase_two_start_board = actual_board

        for i in range(0, len(actual_board[pivot_row])):
            actual_board[pivot_row][i] = actual_board[pivot_row][i] / pivot_element

        operators = get_operators(actual_board=actual_board, pivot_column=pivot_column,
                                  pivot_row=pivot_row)

        for i in range(len(actual_board)):
            for j in range(len(actual_board[pivot_row])):
                if operators[i] is not None and i != pivot_row:
                    actual_board[i][j] = actual_board[i][j] + (actual_board[pivot_row][j] * operators[i])
        it += 1
    return boards, phase_two_start_board, solution_variables


def get_solution_coefficients(solution_variables, variables, function_coefficients):
    solution_coefficients = []
    indexes = []
    for variable in solution_variables:
        if variable in variables:
            indexes.append(variables.index(variable))
    for index in indexes:
        solution_coefficients.append(function_coefficients[index])
    return solution_coefficients


class Simplex:

    @classmethod
    def simplex_two_phases(cls, start_board):
        phase_one_boards, actual_board, solution_variables = solve_phase_one_of_simplex_two_phases(start_board)

        solution_coefficients = get_solution_coefficients(solution_variables=solution_variables,
                                                          variables=start_board.variables,
                                                          function_coefficients=start_board.function_coefficients)
        solution_coefficients.append(' ')
        solution_coefficients.append(' ')
        phase_two_boards = []
        board = copy.deepcopy(start_board)
        indexes = []
        for variable in board.variables:
            if 'A' in variable:
                indexes.append(board.variables.index(variable))

        for row in board.restrictions_coefficients:
            del row[indexes[0]:indexes[-1] + 1]

        del board.variables[indexes[0]:indexes[-1] + 1]

        for row in actual_board:
            del row[indexes[0]:indexes[-1] + 1]

        end = False
        while not end:
            actual_board.append(get_zj(board, actual_board, solution_coefficients))
            actual_board.append(get_optimality_criterion(board, board.function_coefficients, actual_board))
            pivot_column = get_pivot_column(actual_board, 2)
            quotients = get_quotients(board=actual_board, pivot_column=pivot_column)

            minor_quotient = get_minor_quotient(quotients=quotients)

            pivot_row = quotients.index(minor_quotient)
            pivot_element = actual_board[pivot_row][pivot_column]

            phase_two_boards.append(copy.deepcopy(
                get_full_board(board.function_coefficients, board.variables, actual_board, solution_variables,
                               solution_coefficients)))

            solution_variables[pivot_row] = board.variables[pivot_column]
            solution_coefficients[pivot_row] = board.function_coefficients[pivot_column]
            end = end_status(actual_board[-2], 2)
            actual_board.pop()
            actual_board.pop()

            for i in range(0, len(actual_board[pivot_row])):
                actual_board[pivot_row][i] = actual_board[pivot_row][i] / pivot_element

            operators = get_operators(actual_board=actual_board, pivot_column=pivot_column,
                                      pivot_row=pivot_row)

            for i in range(len(actual_board)):
                for j in range(len(actual_board[pivot_row])):
                    if operators[i] is not None and i != pivot_row:
                        actual_board[i][j] = actual_board[i][j] + (actual_board[pivot_row][j] * operators[i])
        return phase_one_boards, phase_two_boards
