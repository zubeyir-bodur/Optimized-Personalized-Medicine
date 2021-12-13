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
    p_sum = -5 * p_in[0] - 0.5 * p_in[1] - 12 * p_in[2] - 8 * p_in[3] - 5 * p_in[4] - 5 * p_in[5] - p_in[6] - 3 * p_in[7] - 2 * p_in[8]
    y_sum = -5 * y_in[0] - 6 * y_in[1] - 4 * y_in[2] - 4 * y_in[3] - 8 * y_in[4] - 6 * y_in[5] - 7 * y_in[6]
    x_sum = 0.28 * x_in[0] + 0.3 * x_in[1] + 0.25 * x_in[2] + 0.17 * x_in[3] + 0.31 * x_in[4] + 0.246 * x_in[5] + 0.4*x_in[6]
    return p_sum + y_sum + x_sum


# Read patient data from .xlsx file
patient_data = pd.read_excel('patient_data.xlsx', sheet_name="Sheet1")

# Read the group number 36
patient_36 = patient_data.iloc[50, :]

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
#fb_i = [0, 0, 0, 0, 0, 0, 0]
#ub_i = [0, 0, 0, 0, 0, 0, 0]

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
M = 5
N = 200
z = []
w = []
g = []
k = []
l = []
m = []
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
    w.append(model.addVar(vtype=GRB.BINARY, name="w" + str(i)))
    g.append(model.addVar(vtype=GRB.BINARY, name="g" + str(i)))
    k.append(model.addVar(vtype=GRB.BINARY, name="k" + str(i)))
    l.append(model.addVar(vtype=GRB.BINARY, name="l" + str(i)))
    m.append(model.addVar(vtype=GRB.INTEGER, lb=-1, ub=1, name="m" + str(i)))

# Set the objective
model.setObjective(quicksum(fb_i[i]*(a[i] + r[i]) + ub_i[i]*c[i] for i in range(0, 7)), GRB.MINIMIZE)

# Add the quality of life constraint
model.addConstr(q(p, y, x) >= Q_36, name="quality_of_life")

# Add the remaining constraints
for i in range(0, 7):
    """
    if y[i]-yb[i] > 0 then a[i] = 1
    """
    model.addConstr(y[i] - yb_i[i], GRB.LESS_EQUAL, M * w[i], name="if_drug_" + str(i+1) + "_is_added")
    model.addConstr(1 - a[i], GRB.LESS_EQUAL, M * (1 - w[i]), name="then_a_" + str(i+1) + "is_1")

    """
    if yb[i]-y[i] > 0 then r[i] = 1
    """
    model.addConstr(yb_i[i] - y[i], GRB.LESS_EQUAL, M * g[i], name="if_drug" + str(i+1) + "_is_removed")
    model.addConstr(1 - r[i], GRB.LESS_EQUAL, M * (1 - g[i]), name="then_r" + str(i+1) + "_is_1")

    """
    if y[i]-yb[i] = 0 then a[i], r[i] = 0, 0 
    """
    model.addConstr(y[i] - yb_i[i], GRB.EQUAL, m[i], name="if_no_change" + str(i + 1))
    model.addConstr(a[i], GRB.LESS_EQUAL, m[i] * m[i], name="then_no_add" + str(i + 1))
    model.addConstr(r[i], GRB.LESS_EQUAL, m[i] * m[i], name="then_no_remove" + str(i + 1))
    """
    if x[i] - xb[i] > 0 then inc[i] = 1
    """
    model.addConstr(x[i] - xb_i[i], GRB.LESS_EQUAL, N * k[i], name="if_dosage" + str(i+1) + "_increased")
    model.addConstr(1 - inc[i], GRB.LESS_EQUAL, N * (1 - k[i]), name="then_incr[" + str(i+1) + "]=1")
    """
    if xb[i] - x[i] > 0 then dec[i] = 1
    """
    model.addConstr(xb_i[i] - x[i], GRB.LESS_EQUAL, N * l[i], name="if_dosage" + str(i+1) + "_decreased")
    model.addConstr(1 - dec[i], GRB.LESS_EQUAL, N * (1 - l[i]), name="then_decr[" + str(i+1) + "]=1")

    """
    inc[i] NAND dec[i] = 1 for all i
    equivalent to inc + dec <= 1
    """
    model.addConstr(inc[i] + dec[i], GRB.LESS_EQUAL, 1, name="inc_nand_dec_" + str(i+1))

    """
    r[i] NAND a[i] = 1 for all i
    equivalent to a + r <= 1
    """
    model.addConstr(a[i] + r[i], GRB.LESS_EQUAL, 1, name="a_nand_r_" + str(i+1))

    """
    c[i] = abs(x - base_regimen_dose)
    """
    model.addConstr(c[i], GRB.EQUAL, (x[i] - xb_i[i]) * (inc[i] - dec[i]), name="change_" + str(i+1))
    """
    Dosage bounds, if y = 0 the interval is [0, 0] = 0
    """
    model.addConstr(x[i], GRB.GREATER_EQUAL, min_i[i] * y[i], name="min_x" + str(i+1))
    model.addConstr(x[i], GRB.LESS_EQUAL, max_i[i] * y[i], name="max_x" + str(i))
    model.update()

# Solve the model
model.write("partb_new.lp")
model.optimize()
model.printAttr('X')
model.update()
print("Decision Variables: ")
for i in range(1, 8):
    print("x" + str(i) + " = " + str(int(round(model.getVarByName("x" + str(i)).getAttr('X')))))
    print("y" + str(i) + " = " + str(int(round(model.getVarByName("y" + str(i)).getAttr('X')))) + "\n")
print("Quality Of Life = " + str(checkQ(p, model)))
print("Deviation Cost, a.k.a. objective  = " + str(int(round(model.getObjective().getValue()))))

print("Quality of Life for base regimen = " + str(q(p, yb_i, xb_i)))
