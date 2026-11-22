"""Linear programming problem definition."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Sense(Enum):
    """Relational operator of a constraint."""

    LE = "<="
    GE = ">="
    EQ = "="


class Goal(Enum):
    """Direction of the objective function."""

    MAX = "max"
    MIN = "min"


@dataclass(frozen=True)
class Constraint:
    """A single linear constraint ``coefficients · x  (<=|>=|=)  rhs``."""

    coefficients: tuple[float, ...]
    sense: Sense
    rhs: float
    name: str = ""


@dataclass(frozen=True)
class LinearProgram:
    """A linear program with non-negative decision variables.

    ``goal  objective · x``  subject to every constraint and ``x >= 0``.
    """

    objective: tuple[float, ...]
    constraints: tuple[Constraint, ...]
    goal: Goal = Goal.MAX
    variable_names: tuple[str, ...] = field(default=())

    def __post_init__(self) -> None:
        n = len(self.objective)
        if n == 0:
            raise ValueError("The objective needs at least one variable.")
        if not self.constraints:
            raise ValueError("The problem needs at least one constraint.")
        for index, constraint in enumerate(self.constraints):
            if len(constraint.coefficients) != n:
                raise ValueError(
                    f"Constraint {index + 1} has {len(constraint.coefficients)} coefficients, expected {n}."
                )
        if self.variable_names and len(self.variable_names) != n:
            raise ValueError("variable_names must have one name per variable.")
        if not self.variable_names:
            object.__setattr__(self, "variable_names", tuple(f"X{i + 1}" for i in range(n)))

    @property
    def num_variables(self) -> int:
        return len(self.objective)

    @property
    def num_constraints(self) -> int:
        return len(self.constraints)

    def constraint_names(self) -> tuple[str, ...]:
        return tuple(c.name or f"R{i + 1}" for i, c in enumerate(self.constraints))
