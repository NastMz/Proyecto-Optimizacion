"""Two-phase simplex method with a full record of every tableau.

The tableau layout follows the classroom convention used in the course:

* ``Cj`` row with the cost of every column,
* one row per basic variable (``CB``, ``VB`` and the constraint coefficients),
* ``Zj`` row (``CB · column``) and ``Cj - Zj`` row (reduced costs).

Phase 1 minimises the sum of the artificial variables; phase 2 optimises the
original objective. Dantzig's rule picks the entering column and Bland's rule
takes over after a run of degenerate pivots, so the method never cycles.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .model import Goal, LinearProgram, Sense

TOLERANCE = 1e-9
MAX_ITERATIONS = 1000
DEGENERATE_PIVOTS_BEFORE_BLAND = 10


class Status(Enum):
    OPTIMAL = "optimal"
    INFEASIBLE = "infeasible"
    UNBOUNDED = "unbounded"


@dataclass(frozen=True)
class Tableau:
    """Snapshot of one simplex iteration, before its pivot is applied."""

    phase: int
    iteration: int
    minimize: bool
    column_names: tuple[str, ...]
    cj: tuple[float, ...]
    basis: tuple[str, ...]
    cb: tuple[float, ...]
    rows: tuple[tuple[float, ...], ...]
    rhs: tuple[float, ...]
    zj: tuple[float, ...]
    z: float
    reduced_costs: tuple[float, ...]
    entering: int | None
    leaving: int | None
    ratios: tuple[float | None, ...]

    @property
    def is_final(self) -> bool:
        return self.entering is None or self.leaving is None


@dataclass(frozen=True)
class StandardForm:
    """``A x = b, x >= 0`` built from a :class:`LinearProgram`.

    Rows with a negative right-hand side are multiplied by -1 (``flips``) so
    that ``b >= 0``. Columns are the decision variables followed by one slack
    (``<=``) or surplus (``>=``) column per inequality. Artificial columns are
    not part of the standard form; they only live inside phase 1.
    """

    matrix: np.ndarray
    rhs: np.ndarray
    cost: np.ndarray
    column_names: tuple[str, ...]
    senses: tuple[Sense, ...]
    flips: tuple[int, ...]
    slack_columns: tuple[int | None, ...]
    num_variables: int


@dataclass(frozen=True)
class SimplexResult:
    status: Status
    values: tuple[float, ...]
    objective: float
    tableaus: tuple[Tableau, ...]
    standard: StandardForm
    basis: tuple[int, ...]
    basis_rows: tuple[int, ...]
    problem: LinearProgram

    @property
    def is_optimal(self) -> bool:
        return self.status is Status.OPTIMAL

    def phase(self, number: int) -> tuple[Tableau, ...]:
        return tuple(t for t in self.tableaus if t.phase == number)


def to_standard_form(problem: LinearProgram) -> StandardForm:
    n = problem.num_variables
    m = problem.num_constraints
    senses: list[Sense] = []
    flips: list[int] = []
    rows: list[list[float]] = []
    rhs: list[float] = []
    for constraint in problem.constraints:
        coefficients = [float(a) for a in constraint.coefficients]
        sense = constraint.sense
        b = float(constraint.rhs)
        flip = 1
        if b < 0:
            coefficients = [-a for a in coefficients]
            b = -b
            flip = -1
            sense = {Sense.LE: Sense.GE, Sense.GE: Sense.LE, Sense.EQ: Sense.EQ}[sense]
        rows.append(coefficients)
        rhs.append(b)
        senses.append(sense)
        flips.append(flip)

    slack_columns: list[int | None] = []
    names = list(problem.variable_names)
    extra: list[list[float]] = []
    for i, sense in enumerate(senses):
        if sense is Sense.EQ:
            slack_columns.append(None)
            continue
        column = [0.0] * m
        column[i] = 1.0 if sense is Sense.LE else -1.0
        extra.append(column)
        slack_columns.append(len(names))
        names.append(f"S{i + 1}")

    matrix = np.array(rows, dtype=float)
    if extra:
        matrix = np.hstack([matrix, np.array(extra, dtype=float).T])
    cost = np.zeros(matrix.shape[1])
    cost[:n] = problem.objective
    return StandardForm(
        matrix=matrix,
        rhs=np.array(rhs, dtype=float),
        cost=cost,
        column_names=tuple(names),
        senses=tuple(senses),
        flips=tuple(flips),
        slack_columns=tuple(slack_columns),
        num_variables=n,
    )


class _Solver:
    """Mutable working tableau shared by both phases."""

    def __init__(self, standard: StandardForm) -> None:
        m, width = standard.matrix.shape
        self.standard = standard
        self.names = list(standard.column_names)
        self.row_ids = list(range(m))
        self.basis: list[int] = []
        artificial: list[list[float]] = []
        for i, sense in enumerate(standard.senses):
            if sense is Sense.LE:
                self.basis.append(standard.slack_columns[i])  # type: ignore[arg-type]
            else:
                column = [0.0] * m
                column[i] = 1.0
                artificial.append(column)
                self.basis.append(width + len(artificial) - 1)
                self.names.append(f"A{len(artificial)}")
        self.num_real = width
        self.matrix = standard.matrix.copy()
        if artificial:
            self.matrix = np.hstack([self.matrix, np.array(artificial, dtype=float).T])
        self.rhs = standard.rhs.copy()
        self.snapshots: list[Tableau] = []

    @property
    def has_artificials(self) -> bool:
        return self.matrix.shape[1] > self.num_real

    def run_phase(self, phase: int, cost: np.ndarray, minimize: bool) -> Status:
        iteration = 0
        degenerate_streak = 0
        while True:
            if iteration > MAX_ITERATIONS:
                raise RuntimeError("The simplex method exceeded the iteration limit.")
            cb = cost[self.basis]
            zj = cb @ self.matrix
            z = float(cb @ self.rhs)
            reduced = cost - zj
            score = -reduced if minimize else reduced
            candidates = [j for j in range(len(cost)) if j not in self.basis and score[j] > TOLERANCE]
            if not candidates:
                self._record(phase, iteration, minimize, cost, cb, zj, z, reduced, None, None, ())
                return Status.OPTIMAL
            if degenerate_streak >= DEGENERATE_PIVOTS_BEFORE_BLAND:
                entering = min(candidates)
            else:
                entering = max(candidates, key=lambda j: (score[j], -j))
            column = self.matrix[:, entering]
            ratios = tuple(
                float(self.rhs[i] / column[i]) if column[i] > TOLERANCE else None for i in range(len(column))
            )
            valid = [i for i, r in enumerate(ratios) if r is not None]
            if not valid:
                self._record(phase, iteration, minimize, cost, cb, zj, z, reduced, entering, None, ratios)
                return Status.UNBOUNDED
            best = min(ratios[i] for i in valid)  # type: ignore[type-var]
            ties = [i for i in valid if ratios[i] - best <= TOLERANCE * max(1.0, abs(best))]  # type: ignore[operator]
            leaving = min(ties, key=lambda i: self.basis[i])
            self._record(phase, iteration, minimize, cost, cb, zj, z, reduced, entering, leaving, ratios)
            degenerate_streak = degenerate_streak + 1 if best <= TOLERANCE else 0
            self.pivot(leaving, entering)
            iteration += 1

    def pivot(self, row: int, column: int) -> None:
        pivot = self.matrix[row, column]
        self.matrix[row] /= pivot
        self.rhs[row] /= pivot
        for i in range(self.matrix.shape[0]):
            if i != row and abs(self.matrix[i, column]) > 0:
                factor = self.matrix[i, column]
                self.matrix[i] -= factor * self.matrix[row]
                self.rhs[i] -= factor * self.rhs[row]
        self.matrix[np.abs(self.matrix) < 1e-12] = 0.0
        self.rhs[np.abs(self.rhs) < 1e-12] = 0.0
        self.basis[row] = column

    def drop_artificials(self) -> None:
        """Pivot zero-level artificials out of the basis, drop redundant rows and artificial columns."""
        row = 0
        while row < len(self.basis):
            if self.basis[row] >= self.num_real:
                candidates = [j for j in range(self.num_real) if abs(self.matrix[row, j]) > TOLERANCE]
                if candidates:
                    self.pivot(row, candidates[0])
                else:
                    self.matrix = np.delete(self.matrix, row, axis=0)
                    self.rhs = np.delete(self.rhs, row)
                    del self.basis[row]
                    del self.row_ids[row]
                    continue
            row += 1
        self.matrix = self.matrix[:, : self.num_real]
        self.names = self.names[: self.num_real]

    def _record(self, phase, iteration, minimize, cost, cb, zj, z, reduced, entering, leaving, ratios) -> None:
        self.snapshots.append(
            Tableau(
                phase=phase,
                iteration=iteration,
                minimize=minimize,
                column_names=tuple(self.names),
                cj=tuple(float(c) for c in cost),
                basis=tuple(self.names[j] for j in self.basis),
                cb=tuple(float(c) for c in cb),
                rows=tuple(tuple(float(v) for v in row) for row in self.matrix),
                rhs=tuple(float(v) for v in self.rhs),
                zj=tuple(float(v) for v in zj),
                z=z,
                reduced_costs=tuple(float(v) for v in reduced),
                entering=entering,
                leaving=leaving,
                ratios=ratios,
            )
        )


def solve(problem: LinearProgram) -> SimplexResult:
    """Solve ``problem`` with the two-phase simplex method."""
    standard = to_standard_form(problem)
    solver = _Solver(standard)
    status = Status.OPTIMAL

    if solver.has_artificials:
        phase_one_cost = np.zeros(solver.matrix.shape[1])
        phase_one_cost[solver.num_real :] = 1.0
        solver.run_phase(1, phase_one_cost, minimize=True)
        if solver.snapshots[-1].z > 1e-7 * max(1.0, float(np.abs(standard.rhs).max())):
            status = Status.INFEASIBLE
        else:
            solver.drop_artificials()

    if status is Status.OPTIMAL:
        status = solver.run_phase(2, standard.cost.copy(), minimize=problem.goal is Goal.MIN)

    values = np.zeros(standard.matrix.shape[1])
    objective = float("nan")
    if status is Status.OPTIMAL:
        for row, column in enumerate(solver.basis):
            values[column] = solver.rhs[row]
        objective = float(standard.cost @ values)
    return SimplexResult(
        status=status,
        values=tuple(float(v) for v in values[: standard.num_variables]),
        objective=objective,
        tableaus=tuple(solver.snapshots),
        standard=standard,
        basis=tuple(solver.basis),
        basis_rows=tuple(solver.row_ids),
        problem=problem,
    )
