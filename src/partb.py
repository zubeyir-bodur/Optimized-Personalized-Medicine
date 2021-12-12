"""
IE 400 Project - Part B
"""
import gurobipy as gp
from gurobipy import GRB
import pandas as pd


def q(p_in, y_in, x_in):
    p_sum = -5*p_in[0] - 0.5*p_in[1] - 12*p_in[2] - 8*p_in[3] - 5*p_in[4] - 5*p_in[5] - p_in[6] - 3*p_in[7] - 2*p_in[8]
    y_sum = -5*y_in[0] - 6*y_in[1] - 4*y_in[2] - 4*y_in[3] - 8*y_in[4] - 6*y_in[5] - 7*y_in[6]
    x_sum = 0.28*x_in[0] + 0.3*x_in[1] + 0.25*x_in[2] + 0.17*x_in[3] + 0.31*x_in[4] + 0.246*x_in[5] + 0.4*x_in[6]
    return p_sum + y_sum + x_sum


# Read patient data from .xlsx file
patient_data = pd.read_excel('patient_data.xlsx', sheet_name="Sheet1")

# Read the group number 36
patient_36 = patient_data.iloc[36, :]

# vector of features
p = list(patient_36[1:10])

# Q threshold
Q_36 = patient_36[10]

# Maximum/Minimum allowed dosages
min_i = [20, 10, 20, 10, 10, 20, 20]
max_i = [80, 50, 100, 100, 70, 90, 50]

# Base regimen specs
yb_i = [1, 0, 1, 1, 0, 0, 1]
xb_i = [20, 0, 30, 15, 0, 0, 35]

# Cost of deviating from the base regimen
fb_i = [25, 50, 10, 25, 20, 30, 40]
ub_i = [1, 2, 1, 3, 2, 1, 1]

# Create a Model instance
model = gp.Model()

# Decision variables - from i = 1 to 7 inclusive
a = []
r = []
m = []
c = []
x = []
y = []
for i in range(1, 8):
    # Add each indexed decision variable one by one
    a.append(model.addVar(vtype=GRB.BINARY, name="a" + str(i)))
    r.append(model.addVar(vtype=GRB.BINARY, name="r" + str(i)))
    m.append(model.addVar(vtype=GRB.BINARY, name="m" + str(i)))
    c.append(model.addVar(vtype=GRB.INTEGER, name="c" + str(i)))
    x.append(model.addVar(vtype=GRB.INTEGER, name="x" + str(i)))
    y.append(model.addVar(vtype=GRB.BINARY, name="y" + str(i)))

# Set the objective
#model.setObjective()

# Add the quality of life constraint
c1 = model.addConstr(q(p, y, x) >= Q_36)

# Add the remaining constraints
for i in range(1, 8):
    c2 = 0
    c3 = 0
    c4 = 0
    c5 = 0
    if i == 2 or i == 5 or i == 6:
        c2 = model.addConstr(y[i-1] == a[i-1])
    if i == 1 or i == 3 or i == 4 or i == 7:
        c3 = model.addConstr(y[i-1] == 1 - r[i-1])
    if i == 1 or i == 3 or i == 4 or i == 7:
        c4 = model.addConstr(a[i-1] == 0)
    if i == 2 or i == 5 or i == 6:
        c5 = model.addConstr(r[i-1] == 0)
    # TODO: change the decision variable m to
    #  binary, then update the model accordingly
    diff = m[i-1] * c[i-1]
    #print(type(diff))
    #set_to = (xb_i[i-1]*y[i-1] + diff * y[i-1])
    #c6 = model.addConstr(x[i-1] == set_to)
    c7 = model.addConstr(x[i-1] >= min_i[i-1])
    c8 = model.addConstr(x[i-1] <= max_i[i-1])
    # Try to imitate a ternary variable for m
    c12 = model.addConstr(m[i-1] >= -1)
    c13 = model.addConstr(m[i-1] <= 1)
    c14 = model.addConstr(c[i-1] >= 0)
    c15 = model.addConstr(x[i-1] >= 0)

# Solve the model
#model.optimize()
#model.printAttr('X')  # This prints the non-zero solutions found




