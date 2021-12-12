"""
IE 400 Project - Part B
"""
import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Read patient data from .xlsx file
patient_data = pd.read_excel('patient_data.xlsx', sheet_name="Sheet1")
# Declare constants

# Solve the minimization problem for each patient
for k in range(1):
    # Create a Model instance
    m = gp.Model()

    # Decision variables
    X1 = m.addVar(vtype=GRB.INTEGER, name="X1")
    X2 = m.addVar(vtype=GRB.INTEGER, name="X2")
    X3 = m.addVar(vtype=GRB.INTEGER, name="X3")
    X4 = m.addVar(vtype=GRB.INTEGER, name="X4")
    X5 = m.addVar(vtype=GRB.INTEGER, name="X5")

    # Providing the coefficients and the sense of the objective function
    m.setObjective(9*X1 + 13*X2 + 10*X3 + 8*X4 + 8*X5, GRB.MINIMIZE)

    # Adding the 6 constraints
    c1 = m.addConstr(6*X1 + 3*X2 + 2*X3 + 4*X4 + 7*X5 >= 40)
    c2 = m.addConstr(X1 <= 1)

    c3 = m.addConstr(X2 >= 1)
    c4 = m.addConstr(X3 >= 2)
    c5 = m.addConstr(X4 >= 1)
    c6 = m.addConstr(X5 <= 3)
    # Solving the model
    m.optimize()
    m.printAttr('X')  # This prints the non-zero solutions found

