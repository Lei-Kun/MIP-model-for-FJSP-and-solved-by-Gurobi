from gurobipy import Model, GRB, quicksum
import sys

def MIPModel(Data):
    n = Data['n']
    m = Data['m']
    J = Data['J']
    OJ = Data['OJ']
    operations_machines = Data['operations_machines']
    operations_times = Data['operations_times']
    largeM = Data['largeM']

    # preprocessing
    # obtain the earliest starting time for each operation
    stimeOp = {}
    stimeOpMax = 0
    for i in J:
        for j in OJ[i]:
            if j == 1:
                stimeOp[i, j] = 0
            else:
                opt_time_min = sys.maxsize
                for k in operations_machines[i, j - 1]:
                    if operations_times[i, j - 1, k] < opt_time_min:
                        opt_time_min = operations_times[i, j - 1, k]
                stimeOp[i, j] = stimeOp[i, j - 1] + opt_time_min
            if stimeOpMax < stimeOp[i, j]:
                stimeOpMax = stimeOp[i, j]
    # print(stimeOp)
    # the latest completion time for each operation
    ltimeOp = {}
    for i in J:
        for jj in range(len(OJ[i]) - 1, -1, -1):
            j = OJ[i][jj]
            opt_time_min = sys.maxsize
            for k in operations_machines[i, j]:
                if operations_times[i, j, k] < opt_time_min:
                    opt_time_min = operations_times[i, j, k]

            if jj == len(OJ[i]) - 1:
                ltimeOp[i, j] = largeM - opt_time_min
            else:
                ltimeOp[i, j] = ltimeOp[i, j + 1] - opt_time_min
    print(ltimeOp)

    model = Model("FJSP_PPF")

    x, y, s = {}, {}, {}
    cmax = model.addVar(lb=stimeOpMax, ub=largeM, vtype="I", name="cmax")
    # define x
    for j in J:  # job
        for i in OJ[j]:  # operation
            # s[j,i]=model.addVar(lb=0,ub=largeM,vtype="I",name="s(%s,%s)"%(j,i))
            s[j, i] = model.addVar(lb=stimeOp[j, i], ub=largeM, vtype="I", name="s(%s,%s)" % (j, i))  # ltimeOp[j,i]
            for k in operations_machines[j, i]:
                x[j, i, k] = model.addVar(lb=0, ub=1, vtype="I", name="x(%s,%s,%s)" % (j, i, k))
    # define y
    for i in J:
        for ip in J:
            for j in OJ[i]:
                for jp in OJ[ip]:
                    y[i, j, ip, jp] = model.addVar(lb=0, ub=1, vtype="I", name="y(%s,%s,%s,%s)" % (i, j, ip, jp))

    # define objective function
    model.setObjective(cmax, GRB.MINIMIZE)
    # constraint(3)
    for i in J:
        for j in OJ[i]:
            model.addConstr(quicksum(x[i, j, k] for k in operations_machines[i, j]) == 1, "assignment(%s,%s)" % (i, j))
    # constraint(4)
    for i in J:
        for j in OJ[i]:
            if j != OJ[i][0]:
                model.addConstr(s[i, j] >= s[i, j - 1] + quicksum(
                    operations_times[i, j - 1, k] * x[i, j - 1, k] for k in operations_machines[i, j - 1]),
                                "stime(%s,%s)" % (i, j))
    # constraint(5)
    for i in J:
        for ip in J:
            if i < ip:
                for j in OJ[i]:
                    for jp in OJ[ip]:
                        kkp = [k for k in operations_machines[i, j] if k in operations_machines[ip, jp]]
                        if len(kkp):
                            for iipk in kkp:
                                model.addConstr(s[ip, jp] >= s[i, j] + operations_times[i, j, iipk] - largeM * (
                                            3 - y[i, j, ip, jp] - x[i, j, iipk] - x[ip, jp, iipk]),
                                                "cons_6_(%s,%s,%s,%s)" % (i, j, ip, jp))
                                model.addConstr(
                                    s[i, j] >= s[ip, jp] +
                                    operations_times[ip, jp, iipk] - largeM *
                                    (2 + y[i, j, ip, jp] - x[i, j, iipk] - x[ip, jp, iipk]),
                                    "cons_5_(%s,%s,%s,%s)" % (i, j, ip, jp))
    # cmax constraint
    for i in J:
        model.addConstr(cmax >= s[i, OJ[i][len(OJ[i]) - 1]] + quicksum(
            operations_times[i, OJ[i][len(OJ[i]) - 1], k] * x[i, OJ[i][len(OJ[i]) - 1], k] for k in
            operations_machines[i, OJ[i][len(OJ[i]) - 1]]), "cmax_cons_(%s)" % (i))



    model.params.TimeLimit=1200
    model.update()
    return model