from docplex.mp.model import Model


def model_szl(p_x1, p_x2, p_x3, p_x4, pm_x1, pm_x2, pm_x3, pm_x4, bill_x1, bill_x2, bill_x3, bill_x4, d_x1, d_x2, d_x3,
              d_x4):
    # Inicializamos el modelo
    mdl = Model('Sazon_Llan')

    # Crear las variables
    x1 = mdl.continuous_var(name='x1')
    x2 = mdl.continuous_var(name='x2')
    x3 = mdl.continuous_var(name='x3')
    x4 = mdl.continuous_var(name='x4')

    # Modelo
    # Función objetiva (Z)
    mdl.maximize(p_x1 * x1 + p_x2 * x2 + p_x3 * x3 + p_x4 * x4)
    # Materia prima
    mdl.add_constraint(12 * x1 <= pm_x1)
    mdl.add_constraint(10 * x2 <= pm_x2)
    mdl.add_constraint(50 * x3 <= pm_x3)
    mdl.add_constraint(60 * x4 <= pm_x4)
    # Presupuesto
    mdl.add_constraint(1421 * x1 <= bill_x1)
    mdl.add_constraint(858 * x2 <= bill_x2)
    mdl.add_constraint(664 * x3 <= bill_x3)
    mdl.add_constraint(1384 * x4 <= bill_x4)
    # Demanda
    mdl.add_constraint(12 * x1 >= d_x1)
    mdl.add_constraint(10 * x2 >= d_x2)
    mdl.add_constraint(50 * x3 >= d_x3)
    mdl.add_constraint(60 * x4 >= d_x4)
    return mdl


class Analysis:
    def __init__(self):
        self.products_name = ['canela', 'clavo', 'uva pasa', 'ajo sal']
        self.constraints_name = ['materia prima canela', 'materia prima clavo', 'materia prima uva pasa',
                                 'materia prima ajo sal', 'presupuesto canela', 'presupuesto clavo',
                                 'presupuesto uva pasa', 'presupuesto ajo sal', 'demanda canela',
                                 'demanda clavo', 'demanda uva pasa', 'demanda ajo sal']

        self.mdl = model_szl(
            p_x1=1918,
            p_x2=1158,
            p_x3=896,
            p_x4=1868,
            pm_x1=19051,
            pm_x2=22680,
            pm_x3=10000,
            pm_x4=3780,
            bill_x1=750000,
            bill_x2=325000,
            bill_x3=325000,
            bill_x4=600000,
            d_x1=10,
            d_x2=10,
            d_x3=4,
            d_x4=6
        )
        self.solution = self.mdl.solve(log_output=True)
        self.number_of_constraints = self.mdl.number_of_constraints
        self.const = [self.mdl.get_constraint_by_index(i) for i in range(self.number_of_constraints)]
        # Reporte de sensibilidad Cplex
        cpx = self.mdl.get_engine().get_cplex()

        # Intervalos coeficientes función objetiva
        self.interval_coefficients = cpx.solution.sensitivity.objective()

        # Intervalos lado derecho
        self.right_interval = cpx.solution.sensitivity.rhs()

    def get_dual_price(self):
        # Precios duales
        precio_dual = self.mdl.dual_values(self.const)
        print("")
        # Imprimir precios duales de cada restricción
        for n in range(self.number_of_constraints):
            print("Si cambia en una unidad el valor de " + self.constraints_name[n] + ", esto lo beneficiara en " +
                  str(precio_dual[n]) + " pesos.")
        return precio_dual

    def get_solution(self):
        self.solution.display()

    def print_intervals_coefficients(self):
        # Imprimir sensibilidad función objetiva:
        print("\n Análisis")
        print(" ")
        for n in range(4):
            print(
                "Usted puede cambiar el valor de " + self.products_name[n] + " entre el intervalo: " + str(
                    self.interval_coefficients[n]))

    def print_right_intervals(self):
        # Imprimir sensibilidad lado derecho:
        print("\n Análisis")
        print(" ")
        for n in range(self.number_of_constraints):
            print(
                "Usted puede cambiar la cantidad de " + self.constraints_name[n] + " entre el intervalo: " + str(
                    self.right_interval[n]))
