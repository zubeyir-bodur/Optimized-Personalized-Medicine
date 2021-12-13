
"""
IE 400 Project - Part B
"""
import gurobipy as gp
from gurobipy import *
import pandas as pd


def checkQ(p_in, my_model):
    y_ = []
    x_ = []
    for i in range(0, 7):
        x_.append(int(round(my_model.getVarByName("x" + str(i + 1)).getAttr('X'))))
        y_.append(int(round(my_model.getVarByName("y" + str(i + 1)).getAttr('X'))))
    return q(p_in, y_, x_)


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
#fb_i = [0, 0, 0, 0, 0, 0, 0]
ub_i = [1, 2, 1, 3, 2, 1, 1]

# Create a Model instance
model = gp.Model()

# Decision variables - from i = 1 to 7 inclusive
a = []
r = []
c = []
x = []
y = []
inc = []
dec = []
M = 2
z = []
for i in range(1, 8):
    # Add each indexed decision variable one by one
    a.append(model.addVar(vtype=GRB.BINARY, name="a" + str(i)))
    r.append(model.addVar(vtype=GRB.BINARY, name="r" + str(i)))
    inc.append(model.addVar(vtype=GRB.BINARY, name="inc" + str(i)))
    dec.append(model.addVar(vtype=GRB.BINARY, name="dec" + str(i)))
    c.append(model.addVar(vtype=GRB.INTEGER, lb=0, name="c" + str(i)))
    x.append(model.addVar(vtype=GRB.INTEGER, lb=0, name="x" + str(i)))
    y.append(model.addVar(vtype=GRB.BINARY, name="y" + str(i)))
    z.append(model.addVar(vtype=GRB.BINARY, name="z" + str(i)))

# Set the objective
model.setObjective(quicksum(fb_i[i-1]*(a[i-1] + r[i-1]) + ub_i[i-1]*c[i-1] for i in range(1, 8)), GRB.MINIMIZE)

# Add the quality of life constraint
model.addConstr(q(p, y, x) >= Q_36, name="quality_of_life")

# Add the remaining constraints
for i in range(1, 8):
    if i == 2 or i == 5 or i == 6:
        model.addConstr(y[i-1] == a[i-1], name="added_drug_" + str(i))
        model.addConstr(r[i-1] == 0, name="already_removed_drug " + str(i))
    if i == 1 or i == 3 or i == 4 or i == 7:
        model.addConstr(y[i-1] == 1 - r[i-1], name="removed_drug " + str(i))
        model.addConstr(a[i-1] == 0, name="already_added_drug " + str(i))

    """
    inc[i] NAND dec[i] = 1 for all i
    model.addConstr(inc[i-1] + dec[i-1] <= 2, name="if_nand_dec_" + str(i))
    """

    """
        inc[i] NAND dec[i] = 1 for all i
    model.addConstr(r[i - 1] + a[i - 1] <= 2, name="a_nand_r_" + str(i))
    """

    """
    If y[i] == 0 then
        inc[i] == 0
        a[i] == 0
    model.addConstr(1 - y[i-1] <= M*z[i-1], name="if_y" + str(i) + "_is_zero")
    model.addConstr(inc[i-1] <= M * (1 - z[i - 1]), name="then_inc" + str(i) + "_must_be_zero")
    model.addConstr(a[i-1] <= M * (1 - z[i - 1]), name="then_a" + str(i) + "_must_be_zero")
    """

    """
    x[i] = base_regimen + change, if included, otherwise zero
    x will be zero if y = 0 as well, compatible with other constraints
    """
    model.addConstr(x[i-1] == (xb_i[i-1]*y[i-1] + (inc[i-1] - dec[i-1])*c[i-1]), name="set_x" + str(i))

    """
    Dosage bounds, if y = 0 the interval is [0, 0] = 0
    """
    model.addConstr(x[i-1] >= min_i[i-1] * y[i-1], name="min_x" + str(i))
    model.addConstr(x[i-1] <= max_i[i-1] * y[i-1], name="max_x" + str(i))
    model.update()

# Solve the model
model.write("partb.lp")
model.optimize()
model.printAttr('X')
model.update()
print("Decision Variables: ")
for i in range(1, 8):
    print("x" + str(i) + " = " + str(int(round(model.getVarByName("x" + str(i)).getAttr('X')))))
    print("y" + str(i) + " = " + str(int(round(model.getVarByName("y" + str(i)).getAttr('X')))) + "\n")
print("Quality Of Life = " + str(checkQ(p, model)))
print("Deviation Cost, a.k.a. objective  = " + str(int(round(model.getObjective().getValue()))))
