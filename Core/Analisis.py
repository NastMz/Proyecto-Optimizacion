# Importar el Cplex
import cplex
from docplex.mp.model import Model


def model_szl():
    # Inicializamos el modelo
    mdl = Model('Sazon_Llan')

    # Crear las variables
    x1 = mdl.continuous_var(name='x1')
    x2 = mdl.continuous_var(name='x2')
    x3 = mdl.continuous_var(name='x3')
    x4 = mdl.continuous_var(name='x4')

    # Modelo
    # Funcion objetico (Z)
    mdl.maximize(1918 * x1 + 1158 * x2 + 896 * x3 + 1868 * x4)
    # Materia prima
    mdl.add_constraint(12 * x1 <= 19051)
    mdl.add_constraint(10 * x2 <= 22680)
    mdl.add_constraint(50 * x3 <= 10000)
    mdl.add_constraint(60 * x4 <= 3780)
    # Presupuesto
    mdl.add_constraint(1421 * x1 <= 750000)
    mdl.add_constraint(858 * x2 <= 325000)
    mdl.add_constraint(664 * x3 <= 325000)
    mdl.add_constraint(1384 * x4 <= 600000)
    # Demanda
    mdl.add_constraint(12 * x1 >= 10)
    mdl.add_constraint(10 * x2 >= 10)
    mdl.add_constraint(50 * x3 >= 4)
    mdl.add_constraint(60 * x4 >= 6)
    solucion = mdl.solve(log_output=True)
    return mdl, solucion


def get_solution(mdl):
    solucion = mdl.solve(log_output=True)
    solucion.display()
    return solucion


def n_restriction(mdl):
    n_const = mdl.number_of_constraints
    return n_const


def restrictions(mdl, n_const):
    const = [mdl.get_constraint_by_index(i) for i in range(n_const)]
    return const


"""
# Variables de Holgura
h = mdl.slack_values(const)
h

# Imprimir variables de Holgura de cada restricción
for n in range(n_const):
    print("La variable de holgura de la restriccion (" + str(const[n]) + ") es = " + str(h[n]))
"""





def intervals(mdl):
    # Reporte de sensibilidad Cplex
    cpx = mdl.get_engine().get_cplex()

    # Intervalos coeficientes funcion objetivo
    interv_coef = cpx.solution.sensitivity.objective()

    # Intervalos lado derecho
    interv_derech = cpx.solution.sensitivity.rhs()

    return interv_coef, interv_derech


def set_var_list(mdl):
    # Crear una lista con las variables
    var_list = [mdl.get_var_by_name('x1'), mdl.get_var_by_name('x2'),
                mdl.get_var_by_name('x3'), mdl.get_var_by_name('x4')]
    return var_list




"""# Imprimir sensibilidad funcion objetivo:
print("\n Analisis")
print(" ")
for n in range(len(var_list)):
    print("Usted puede cambiar el valor de " + nomb_productos[n] + " entre el intervalo: " + str(interv_coef[n]))

# Imprimir sensibilidad lado derecho:
print("\n Analisis")
print(" ")
for n in range(n_const):
    print("Usted puede cambiar la cantidad de " + nomb_restricciones[n] + " entre el intervalo: " + str(interv_derech[n]))
"""

class Analisis:
    def __init__(self):
        self.nomb_productos = ['canela', 'clavo', 'uva pasa', 'ajo sal']
        self.nomb_restricciones = ['materia prima canela', 'materia prima clavo', 'materia prima uva pasa',
                                  'materia prima ajo sal', 'presupuesto canela', 'presupuesto clavo',
                                  'presupuesto uva pasa', 'presupuesto ajo sal', 'demanda canela',
                                  'demanda clavo', 'demanda uva pasa', 'demanda ajo sal']

    def get_dualprice(self, mdl, n_const, const):
        # Precios duales
        precio_dual = mdl.dual_values(const)
        print("")
        # Imprimir precios duales de cada restricción
        for n in range(n_const):
            print("Si cambia en una unidad el valor de " + self.nomb_restricciones[n] + ", esto lo beneficiara en " + str(
                precio_dual[n]) + " pesos.")
        return precio_dual


