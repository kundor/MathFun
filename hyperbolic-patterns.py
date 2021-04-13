"""
Draw repeating patterns on the hyperbolic plane, in the Poincare disk model.
Implementing "Creating Repeating Hyperbolic Patterns" by Dunham, Lindgren, and Witte,
Computer Graphics Vol. 15 No. 3, August 1981 pp. 215--223.
"""
import numpy as np
import turtle
from math import sin, cos, sinh, cosh, acosh, sqrt, pi
from enum import Enum

class ACTION(Enum):
    Move = 1
    Draw = 2

p = int(input('p (number of sides of p-gon)? '))
q = int(input('q (number of p-gons at a vertex)? '))
assert (p - 2)*(q - 2) > 4, "Not possible to tile hyperbolic tiling with these values"

symtype = 0
while symtype not in (1, 2, 3, 4):
    symtype = int(input('''Choose symmetry type:
    1. [p,q]
    2. [p,q]+
    3. [p+,q]
    4. [p,q+]
    '''))

coshb = cos(pi/q) / sin(pi/p)
b = acosh(coshb)

# "The transformations used in our program are represented by 3-by-3 real matrices.
# For instance, reflections across the sides of the triangular fundamental region for
# the group [p,q] can be represented by:

ReflectEdgeBisector = np.array([[1, 0, 0],
                                [0,-1, 0],
                                [0, 0, 1]])
ReflectPgonEdge = np.array([[-cosh(2*b), 0, sinh(2*b)],
                            [0, 1, 0],
                            [-sinh(2*b), 0, cosh(2*b)]])
ReflectHypotenuse = np.array([[cos(2/p), sin(2/p), 0],
                              [sin(2/p),-cos(2/p),0],
                              [0, 0, 1]])
# where cosh(b) = cos(π/q) / sin(π/p, cosh(2b) = 2*cosh(b)**2 - 1, sinh(2b) = sqrt(cosh(2b)**2 - 1)."

RotateP = ReflectEdgeBisector @ ReflectHypotenuse
RotateQ = ReflectHypotenuse @ ReflectPgonEdge
RotateEdge = ReflectPgonEdge @ ReflectEdgeBisector

Identity = np.eye(3)

def DrawPgonPattern(T):
    for x, y, action in zip(X, Y, Action):
        if isinstance(action, (str, tuple, list)):
            turtle.color(action)
            continue
        SumSquare = x*x + y*y
        Z = np.array([2*x / (1 - SumSquare),
                      2*y / (1 - SumSquare),
                     (1 + SumSquare) / (1 - SumSquare)])
        Z = T @ Z
        Tx, Ty  = Z[:2] / (1 + Z[2])
        if action is ACTION.Move:
            turtle.penup()
            turtle.goto(Tx, Ty)
        elif action is ACTION.Draw:
            turtle.pendown()
            turtle.goto(Tx, Ty)

# Interactive motif generation goes here
# "Once the group has been chosen, the corresponding fundamental region is displayed
# on the graphic screen. The natural boundaries (i.e. lines of reflective symmetry)
# of the fundamental region are drawn as solid lines; the other edges (where the
# interactive "boundary procedure" applies) are drawn as dashed lines. Copies of the
# fundamental regions which are adjacent to the original fundamental region across
# non-reflecting edges are outlined with solid lines (corresponding to other reflection
# lines) and dotted lines. There are zero, three, two, and two of these adjacent copies
# of the fundamental region corresponding to the groups [p,q], [p,q]+, [p+,q], and [p,q+]
# respectively.
# The second step is the creation of the motif within the fundamental region. In the case
# of the group [p,q], this is a straightforward process of moving and drawing, using a
# cursor (since the fundamental region has natural boundaries).
# The second step for the other groups is more interesting, since it is possible to draw
# line segments across the non-reflecting edges of the fundamental region."
# "During the second step, the moves, draws, and color changes are stored in three arrays:
# Action, which records the action taken, and X and Y which record the terminal location
# of the action (terminal location = initial location for a color change.)"

Action = [ACTION.Move, ACTION.Draw, ACTION.Draw, ACTION.Draw]
X = [5, 25, 40, 35]
Y = [5, 15, 40, 35]
