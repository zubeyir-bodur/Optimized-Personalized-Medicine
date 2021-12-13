
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
ub_i = [1, 2, 1, 3, 2, 1, 1]

# Create a Model instance
model = gp.Model()

# Decision variables - from i = 1 to 7 inclusive
a = []
c = []
x = []
y = []
inc = []
dec = []
for i in range(1, 8):
    # Add each indexed decision variable one by one
    a.append(model.addVar(vtype=GRB.BINARY, name="a" + str(i)))
    inc.append(model.addVar(vtype=GRB.BINARY, name="inc" + str(i)))
    dec.append(model.addVar(vtype=GRB.BINARY, name="dec" + str(i)))
    c.append(model.addVar(vtype=GRB.INTEGER, lb=0, name="c" + str(i)))
    x.append(model.addVar(vtype=GRB.INTEGER, lb=0, name="x" + str(i)))
    y.append(model.addVar(vtype=GRB.BINARY, name="y" + str(i)))

# Set the objective
model.setObjective(quicksum(fb_i[i]*a[i] + ub_i[i]*c[i] for i in range(0, 7)), GRB.MINIMIZE)

# Add the quality of life constraint
model.addConstr(q(p, y, x) >= Q_36, name="quality_of_life")

# Add the remaining constraints
for i in range(0, 7):
    if yb_i[i] == 0:
        model.addConstr(a[i] == y[i], name="added_drug_" + str(i+1))
    if yb_i[i] == 1:
        model.addConstr(a[i] == 1 - y[i], name="removed_drug_" + str(i+1))

    """
        inc[i] NAND dec[i] = 1
    """
    model.addConstr(inc[i] + dec[i] <= 1, name="if_nand_dec_" + str(i+1))

    """
    x[i] = base_regimen + change
    
    if y[i] = 0, then
        x[i] = 0 (next constraint)
        inc[i] = 0
        c[i] = xb_i[i]
        if xb_i != 0, then 
            dec[i] = 1
        if xb_i = 0, then 
            dec[i] = 0
    
    if y[i] = 1, then
        min[i]           <= x[i]                     <= max[i] (next constraint)
        min[i] - xb_i[i] <= c[i] * (inc[i] - dec[i]) <= max[i] - xb_i[i]
        if xb_i = 0, then 
            (inc[i], dec[i]) = (1, 0)
        if xb_i != 0, then
            (inc[i], dec[i]) = (0, 0), (0, 1) or (1, 0)
    """
    model.addConstr(x[i] - xb_i[i] == (inc[i] - dec[i])*c[i], name="set_x" + str(i+1))

    """
    Dosage bounds, if y = 0 the interval is [0, 0] = 0
    """
    model.addConstr(x[i] >= min_i[i] * y[i], name="min_x" + str(i+1))
    model.addConstr(x[i] <= max_i[i] * y[i], name="max_x" + str(i+1))
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
