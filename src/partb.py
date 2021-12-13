"""
IE 400 Project - Part B
"""
import gurobipy as gp
from gurobipy import *
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
M = 2
z = []
w = []
g = []
for i in range(0, 7):
    # Add each indexed decision variable one by one
    a.append(model.addVar(vtype=GRB.BINARY, name="a" + str(i+1)))
    r.append(model.addVar(vtype=GRB.BINARY, name="r" + str(i+1)))
    m.append(model.addVar(vtype=GRB.SEMIINT, lb=-1, ub=1, name="m" + str(i+1)))
    c.append(model.addVar(vtype=GRB.SEMIINT, lb=0, name="c" + str(i+1)))
    x.append(model.addVar(vtype=GRB.SEMIINT, lb=0, name="x" + str(i+1)))
    y.append(model.addVar(vtype=GRB.BINARY, name="y" + str(i+1)))
    z.append(model.addVar(vtype=GRB.BINARY, name="z" + str(i+1)))
    w.append(model.addVar(vtype=GRB.BINARY, name="w" + str(i+1)))
    g.append(model.addVar(vtype=GRB.BINARY, name="g" + str(i+1)))

# Set the objective
model.setObjective(quicksum(fb_i[i]*(a[i] + r[i]) + ub_i[i]*c[i] for i in range(0, 7)), GRB.MINIMIZE)

# Add the quality of life constraint
model.addConstr(q(p, y, x) >= Q_36, name="q_of_life")

# Add the remaining constraints
for i in range(0, 7):
    model.addConstr(y[i] - yb_i[i], GRB.LESS_EQUAL, M * w[i], name ="if_drug_" + str(i) + "_is_added")
    model.addConstr(1 - a[i], GRB.LESS_EQUAL, M * (1 - w[i]), name="then_a_" + str(i) + "is_1")
    model.addConstr(r[i], GRB.LESS_EQUAL, M * (1 - w[i]), name="then_r_" + str(i) + "is_0")

    model.addConstr(yb_i[i] - y[i], GRB.LESS_EQUAL, M * g[i], name="if_drug_" + str(i) + "_is_removed")
    model.addConstr(1 - r[i], GRB.LESS_EQUAL, M * (1 - g[i]), name="then_r_" + str(i) + "is_1")
    model.addConstr(a[i], GRB.LESS_EQUAL, M * (1 - g[i]), name="then_a_" + str(i) + "is_0")
    """
    if i == 2 or i == 5 or i == 6:
        model.addConstr(y[i]], GRB.EQUAL, a[i]], name="addition" + str(i+1))
        model.addConstr(r[i]], GRB.EQUAL, 0, name="removal_no" + str(i+1))
    if i == 1 or i == 3 or i == 4 or i == 7:
        model.addConstr(y[i]], GRB.EQUAL, 1 - r[i]], name="removal" + str(i+1))
        model.addConstr(a[i]], GRB.EQUAL, 0, name="addition_no" + str(i+1))
    """
    model.addConstr(x[i], GRB.EQUAL, xb_i[i]*y[i] + m[i] * c[i], name="set_x" + str(i+1))
    model.addConstr(x[i], GRB.GREATER_EQUAL, min_i[i] * y[i], name="min_x" + str(i+1))
    model.addConstr(x[i], GRB.LESS_EQUAL,  max_i[i], name="max_X" + str(i+1))
    """
        If y[i] == 0 then
            m[i] == 0
    """
    model.addConstr(1 - y[i], GRB.LESS_EQUAL,M * z[i], name="if y" + str(i+1) + " is zero")
    model.addConstr(m[i], GRB.LESS_EQUAL,M * (1 - z[i]), name="then m" + str(i+1) + " must be zero")
    model.update()
# Solve the model
model.setParam("NonConvex", 2)
model.optimize()
model.update()
for i in range(1, 8):
    print("x" + str(i) + " = " + str(model.getVarByName("x" + str(i)).getAttr('X')) )
    print("y" + str(i) + " = " + str(model.getVarByName("y" + str(i)).getAttr('X')) + "\n")

def checkQ(p_in, my_model):
    y_ = []
    x_ = []
    for i in range(0, 7):
        x_.append(my_model.getVarByName("x" + str(i + 1)).getAttr('X'))
        y_.append(my_model.getVarByName("y" + str(i + 1)).getAttr('X'))
    return q(p_in, y_, x_)


print("Quality Of Life = " + str(checkQ(p, model)) )