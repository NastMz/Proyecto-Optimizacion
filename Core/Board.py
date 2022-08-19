class Board:
    def __init__(self, variables, solution_variables, solution_coefficients,
                 function_coefficients, restrictions_coefficients, function_phase_one_coefficients):
        self.solution_coefficients = solution_coefficients
        self.solution_variables = solution_variables
        self.restrictions_coefficients = restrictions_coefficients
        self.function_coefficients = function_coefficients
        self.variables = variables
        self.function_phase_one_coefficients = function_phase_one_coefficients
