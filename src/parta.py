"""
IE 400 Project - Part A
"""
import gurobipy as gp
from gurobipy import *
import pandas as pd


def q(p_in, y_in, x_in):
    p_sum = -5 * p_in[0] - 0.5 * p_in[1] - 12 * p_in[2] - 8 * p_in[3] - 5 * p_in[4] - 5 * p_in[5] - p_in[6] - 3 * p_in[7] - 2 * p_in[8]
    y_sum = -5 * y_in[0] - 6 * y_in[1] - 4 * y_in[2] - 4 * y_in[3] - 8 * y_in[4] - 6 * y_in[5] - 7 * y_in[6]
    x_sum = 0.28 * x_in[0] + 0.3 * x_in[1] + 0.25 * x_in[2] + 0.17 * x_in[3] + 0.31 * x_in[4] + 0.246 * x_in[5] + 0.4 * x_in[6]
    return p_sum + y_sum + x_sum


# Read patient data from .xlsx file
patient_data = pd.read_excel('patient_data.xlsx', sheet_name="Sheet1")

# Read the group number 36
patient_36 = patient_data.iloc[36, :]

# vector of features
p = list(patient_36[1:10])

# Q threshold
Q_36 = float(patient_36[10])

print("Group Number: " + str(patient_36[0]))
print("Patient vector: " + str(p))
print("Q threshold: " + str(Q_36))
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
x = []
for i in range(1, 8):
    # Add each indexed decision variable one by one
    x.append(model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="x" + str(i)))

# Set the objective
model.setObjective(q(p, yb_i, x), GRB.MAXIMIZE)


# Add the remaining constraints
for i in range(0, 7):

    """
    Dosage bounds, if y = 0 the interval is [0, 0] = 0
    """
    if i == 0 or i == 2 or i== 3 or i ==6:
        model.addConstr(x[i] >= min_i[i], name="min" + str(i+1))
        model.addConstr(x[i] <= max_i[i], name="max" + str(i + 1))
    else :
        model.addConstr(x[i], GRB.EQUAL, 0, name="set" +str(i+1))
    model.update()

# Solve the model
model.write("parta.lp")
model.optimize()
model.printAttr('X')
model.update()
print("Decision Variables, x and y: ")
for i in range(1, 8):
    print("x" + str(i) + " = " + str(model.getVarByName("x" + str(i)).getAttr('X')))
    print("y" + str(i) + " = " + str(yb_i[i-1]) + "\n")
print("Quality of Life, a.k.a. objective  = " + str(model.getObjective().getValue()))
