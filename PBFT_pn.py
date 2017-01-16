import spnp


def construct_cx_guard(x, N, f):
    pname = []
    for y in range(1, N):
        if y == x:
            continue
        pname.append("P" + str(y) + str(x) + "_")

    def CIGuard(pn):
        token_sum = 0
        for p in pname:
            token_sum += pn.token(p)
        return token_sum >= 2 * f

    return CIGuard, pname


def construct_rx_guard(x, N, f):
    pname = []
    for y in range(0, N):
        if y == x:
            continue
        pname.append("C" + str(y) + str(x) + "_")

    def RIGuard(pn):
        token_sum = 0
        for p in pname:
            token_sum += pn.token(p)
        return token_sum >= 2 * f

    return RIGuard, pname


def construct_ri_guard(N, f):
    pname = []
    for y in range(0, N):
        pname.append("R" + str(y) + "_")

    def RIGuard(pn):
        token_sum = 0
        for p in pname:
            token_sum += pn.token(p)
        return token_sum >= f + 1

    return RIGuard, pname


def pbft_pn_creator(N, f):
    pn = spnp.PetriNet()
    pn.add_place(("Start", 1))
    Tx = 763.8
    Pr = 5946.34

    PP_in = []
    for i in range(1, N):
        istr = str(i)
        PPname = "PP" + istr
        pn.add_exp_trans(PPname + "Tx", Tx, in_arc=[PPname], out_arc=[PPname + "_"])
        PP_in.append(PPname)
        Pij_in = []
        for j in range(0, N):
            if i == j:
                continue
            jstr = str(j)
            Pname = "P" + istr + jstr
            pn.add_exp_trans(Pname + "Tx", Tx, in_arc=[Pname], out_arc=[Pname + "_"])
            Pij_in.append(Pname)

        pn.add_exp_trans("P" + istr + "Pr", Pr, in_arc=[PPname + "_"], out_arc=Pij_in)
    pn.add_exp_trans("PP0Pr", Pr, in_arc=["Start"], out_arc=PP_in)

    for i in range(0, N):
        istr = str(i)
        guard, names = construct_rx_guard(i, N, f)
        pn.add_exp_trans("R" + istr + "Pr", Pr, in_arc=["R" + istr], out_arc=["R" + istr + "_"],
                         guard=guard, tag=names)
        pn.set_init_token("R" + istr, 1)
        Cij_in = []
        for j in range(0, N):
            if i == j:
                continue
            jstr = str(j)
            Cname = "C" + istr + jstr
            pn.add_exp_trans(Cname + "Tx", Tx, in_arc=[Cname], out_arc=[Cname + "_"])
            Cij_in.append(Cname)
        guard, names = construct_cx_guard(i, N, f)
        pn.add_exp_trans("C" + istr + "Pr", Pr, in_arc=["C" + istr], out_arc=Cij_in,
                         guard=guard, tag=names)
        pn.set_init_token("C" + istr, 1)
    guard, names = construct_ri_guard(N, f)
    pn.add_imme_trans("Ri", in_arc=["Rd"], out_arc=["Done"],
                      guard=guard, tag=names)
    pn.set_init_token("Rd", 1)
    pn.set_halt_condition(lambda x: x.token("Done") == 1)
    return pn

def approx_cx_guard(x, N, f):
    name = "C" + str(x)
    def cx_guard(x):
        return x.token(name) >= 2 * f
    return cx_guard, name

def approx_dx_guard(x, N, f):
    name = "D" + str(x)
    def dx_guard(x):
        return x.token(name) >= 2 * f
    return dx_guard, name

def approx_di_guard(N, f):
    namelist = []
    for i in range(0, N):
        namelist.append("D"+str(i)+"_")
    def di_guard(x):
        token_sum = 0
        for n in namelist:
            token_sum += x.token(n)
        return token_sum >= f + 1
    return di_guard, namelist

def pbft_pn_approx(N, f):
    pn = spnp.PetriNet()
    Tx = 763.8
    Pr = 5946.34
    pn.add_exp_trans("PP0Pr", Pr, in_arc=["Start"], out_arc=["PP"])
    pn.set_init_token("Start", 1)
    P_in = []
    for i in range(1, N):
        istr = str(i)
        Pname = "P" + istr
        pn.add_exp_trans(Pname + "Pr", Pr, in_arc=[Pname], out_arc=[Pname + "_"])
        P_in.append(Pname)
        Cname = []
        for j in range(0, N):
            jstr = str(j)
            if i != j:
                Cname.append("C" + jstr)
        pn.add_exp_trans(Pname + "Tx", Tx, in_arc=[Pname + "_"], out_arc=Cname)
    pn.add_exp_trans("PP0Tx", Tx, in_arc=["PP"], out_arc=P_in)

    for i in range(0, N):
        istr = str(i)
        Cname = "C" + istr
        guard, tag = approx_cx_guard(i, N, f)
        pn.add_exp_trans(Cname + "Pr", Pr, in_arc=["PC" + istr],
                         out_arc=[Cname + "_"],
                         guard=guard,
                         tag=tag)
        pn.set_init_token("PC" + istr, 1)
        Dname = []
        for j in range(0, N):
            if i != j:
                jstr = str(j)
                Dname.append("D"+jstr)
        pn.add_exp_trans(Cname+"Tx", Tx, in_arc=[Cname+"_"],
                         out_arc=Dname)

    for i in range(0, N):
        istr = str(i)
        Dname = "D" + istr
        guard, tag = approx_dx_guard(i, N, f)
        pn.add_imme_trans(Dname+"i", in_arc=["PD"+istr],
                          out_arc=[Dname+"_"],
                          guard=guard,
                          tag=tag)
        pn.set_init_token("PD"+istr, 1)

    guard, tag = approx_di_guard(N, f)
    pn.add_imme_trans("Di", in_arc=["PD"],
                      out_arc=["Done"],
                      guard=guard,
                      tag=tag)
    pn.set_init_token("PD", 1)
    pn.set_halt_condition(lambda x : x.token("Done") == 1)
    return pn

param_pair = [(1,4), (2, 7), (3, 10)]
for f, N in param_pair:
    pn = pbft_pn_approx(N, f)
    #G = pn.to_agraph()
    #G.layout(prog="dot")
    #G.draw("PBFT.svg")
    #pn.measure_MTTA()
    #pn.add_cum_reward_func("holding time", lambda x : x.token("PD"))
    #pn.solve()
    print(spnp.compute_acyclic_mtta(pn))

    #for name, val in pn.get_rewards():
    #    print(name, val)
#pn = pbft_pn_creator(4, 1)
#pn.measure_MTTA()
#pn.solve()
#for name, val in pn.get_rewards():
# print(name, val)
