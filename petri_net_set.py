from spnp import *


def two_timesf(name, f):
    def func(q):
        if q.token(name) >= 2 * f:
            return True
        else:
            return False

    return func


def test_pn_blockchain():
    pn = PetriNet()
    pn.set_option(max_iteration=100, precision=1e-10)
    pn.add_place([("Start", 1), "PP",
                  "P1", "P2", "P3",
                  "P1p", "P2p", "P3p",
                  "C3", "C2", "C1", "C0",
                  "C0p", "C1p", "C2p", "C3p",
                  "R0", "R1", "R2", "R3",
                  "Rall", "Done",
                  ("PC0", 1), ("PC1", 1), ("PC2", 1), ("PC3", 1),
                  ("PR1", 1), ("PR2", 1), ("PR3", 1), ("PR4", 1),
                  ("PF", 1)])

    ThinkRate = 5946.34
    TxRate = 763.80
    f = 1
    pn.add_imme_trans("Ri", guard=lambda x: x.token("Rall") >= f + 1,
                      in_arc=["PF"],
                      out_arc=["Done"])
    pn.add_exp_trans("PP0th", ThinkRate, in_arc=["Start"], out_arc=["PP"])
    pn.add_exp_trans("PP0tx", TxRate, in_arc=["PP"], out_arc=["P1", "P2", "P3"])
    pn.add_exp_trans("P1th", ThinkRate, in_arc=["P1"], out_arc=["P1p"])
    pn.add_exp_trans("P2th", ThinkRate, in_arc=["P2"], out_arc=["P2p"])
    pn.add_exp_trans("P3th", ThinkRate, in_arc=["P3"], out_arc=["P3p"])
    pn.add_exp_trans("P1tx", TxRate, in_arc=["P1p"], out_arc=["C0", "C2", "C3"])
    pn.add_exp_trans("P2tx", TxRate, in_arc=["P2p"], out_arc=["C0", "C1", "C3"])
    pn.add_exp_trans("P3tx", TxRate, in_arc=["P3p"], out_arc=["C0", "C1", "C2"])
    pn.add_exp_trans("C0th", ThinkRate, in_arc=["PC0"], out_arc=["C0p"], guard=two_timesf("C0", f))
    pn.add_exp_trans("C1th", ThinkRate, in_arc=["PC1"], out_arc=["C1p"], guard=two_timesf("C1", f))
    pn.add_exp_trans("C2th", ThinkRate, in_arc=["PC2"], out_arc=["C2p"], guard=two_timesf("C2", f))
    pn.add_exp_trans("C3th", ThinkRate, in_arc=["PC3"], out_arc=["C3p"], guard=two_timesf("C3", f))
    pn.add_exp_trans("C0tx", TxRate, in_arc=["C0p"], out_arc=["R1", "R2", "R3"])
    pn.add_exp_trans("C1tx", TxRate, in_arc=["C1p"], out_arc=["R0", "R2", "R3"])
    pn.add_exp_trans("C2tx", TxRate, in_arc=["C2p"], out_arc=["R0", "R1", "R3"])
    pn.add_exp_trans("C3tx", TxRate, in_arc=["C3p"], out_arc=["R0", "R1", "R2"])
    pn.add_imme_trans("R0th", in_arc=["PR1"], out_arc=["Rall"], guard=two_timesf("R0", f))
    pn.add_imme_trans("R1th", in_arc=["PR2"], out_arc=["Rall"], guard=two_timesf("R1", f))
    pn.add_imme_trans("R2th", in_arc=["PR3"], out_arc=["Rall"], guard=two_timesf("R2", f))
    pn.add_imme_trans("R3th", in_arc=["PR4"], out_arc=["Rall"], guard=two_timesf("R3", f))
    pn.set_halt_condition(lambda x: True if x.token("Done") != 0 else False)
    place_of_interest = ["C0", "C1", "C2", "C3", "R0", "R1", "R2", "R3", "Rall"]
    for p in place_of_interest:
        pn.add_inst_reward_func(p, lambda x, p=p: x.token(p))
    pn.add_cum_reward_func("mtta", lambda x: 0 if x.is_absorbing() else 1)
    return pn


def mtta_func(x):
    if x.is_absorbing():
        return 0
    else:
        return 1

def get_two(x):
    return 2.0

def get_one(x):
    return 1.0

def test_pn_two_stages():
    pn = PetriNet()
    pn.set_option(max_iteration=10, precision=1e-20)
    pn.add_exp_trans("t1", get_one, in_arc=["p1"], out_arc=["p2"])
    pn.add_exp_trans("t2", lambda x : 1, in_arc=["p2"], out_arc=["p3"])
    pn.set_init_token("p1", 1)
    pn.add_cum_reward_func("mtta", mtta_func)
    return pn


def test_pn_slip_away():
    pn = PetriNet()
    pn.set_option(max_iteration=10000, precision=1e-10)
    pn.add_place([("p1", 1), "p2", "p3"])
    pn.add_exp_trans("t1", get_two,
                     in_arc=["p1"],
                     out_arc=["p2"])
    pn.add_exp_trans("t2", 1,
                     in_arc=["p2"],
                     out_arc=["p1"])
    pn.add_exp_trans("t3", 0.1,
                     in_arc=["p2"],
                     out_arc=["p3"])
    pn.add_inst_reward_func("all", lambda x: x.token("p3"))
    pn.add_cum_reward_func("mtta", mtta_func)
    return pn


def test_pn_birth_death():
    pn = PetriNet()
    pn.set_option(max_iteration=1000, precision=1e-10)
    pn.add_place([("p1", 20), "p2"])
    pn.add_exp_trans("t1", 0.1,
                     in_arc=["p1"],
                     out_arc=["p2"])
    pn.add_exp_trans("t2", 0.2,
                     in_arc=["p2"],
                     out_arc=["p1"])
    pn.add_inst_reward_func("up", lambda x: 1 if x.token("p1") != 0 else 0)
    return pn


def test_pn_two_class1():
    pn = PetriNet()
    pn.add_place(["a1", "a2", ("o1", 1), "o2"])
    pn.add_exp_trans("ta1", 0.1, in_arc=["a1"], out_arc=["a2"])
    pn.add_exp_trans("ta2", 0.2, in_arc=["a2"], out_arc=["a1"])
    pn.add_exp_trans("to1", 0.2, in_arc=["o1"], out_arc=["o2"])
    pn.add_exp_trans("to2", 0.1, in_arc=["o2"], out_arc=["o1"])
    pn.measure_place_nonempty_prob()
    pn.measure_MTTA()
    return pn


def test_pn_two_class2():
    pn = PetriNet()
    pn.add_place([("a", 1), "b", "c"])
    pn.add_exp_trans("tab", 0.1, in_arc=["a"], out_arc=["b"])
    pn.add_exp_trans("tbc", 0.2, in_arc=["b"], out_arc=["c"])
    pn.add_exp_trans("tcb", 0.4, in_arc=["c"], out_arc=["b"])
    pn.measure_place_nonempty_prob()
    pn.measure_MTTA()
    return pn

def test_pn_three_class1():
    pn = PetriNet()
    pn.add_place([("a", 1), "b",
                  "c", "d",
                  "e", "f",
                  ])
    pn.add_exp_trans("tab", 0.1, in_arc=["a"], out_arc=["b"])
    pn.add_exp_trans("tba", 0.1, in_arc=["b"], out_arc=["a"])
    pn.add_exp_trans("tcd", 0.1, in_arc=["c"], out_arc=["d"])
    pn.add_exp_trans("tdc", 0.1, in_arc=["d"], out_arc=["c"])
    pn.add_exp_trans("tef", 0.1, in_arc=["e"], out_arc=["f"])
    pn.add_exp_trans("tfe", 0.1, in_arc=["f"], out_arc=["e"])

    pn.add_exp_trans("tac", 100, in_arc=["a"], out_arc=["c"])
    pn.add_exp_trans("tbe", 100, in_arc=["b"], out_arc=["e"])
    pn.measure_place_nonempty_prob()
    pn.measure_MTTA()
    return pn

def test_pn_three_class2():
    pn = test_pn_three_class1()
    pn.set_init_token("a", 0)
    pn.set_init_token("b", 1)
    return pn

pn_creator_func = []
name_dict = dict(globals())
for func_name, func in name_dict.items():
    if func_name.startswith("test_pn_"):
        pn_creator_func.append((func_name[5:], func))
