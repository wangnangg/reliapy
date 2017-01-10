from spnp import *

f = 1
def one_moref(name):
    def func(q):
        if q.token(name) >= f + 1:
            return True
        else:
            return False
    return func

def two_timesf(name):
    def func(q):
        if q.token(name) >= 2 * f:
            return True
        else:
            return False
    return func

def place_token(name):
    def func(q):
        return q.token(name)
    return func

def test_blockchain_pn():
    pn = PetriNet()
    pn.add_place([("Start",1),"PP",
                  "P1", "P2", "P3",
                  "P1p", "P2p", "P3p",
                  "C3", "C2", "C1", "C0",
                  "C0p","C1p", "C2p", "C3p",
                  "R0", "R1", "R2", "R3",
                  "Rall", "Done",
                  ("PC0", 1), ("PC1",1), ("PC2",1), ("PC3",1),
                  ("PR1",1),("PR2",1),("PR3",1), ("PR4",1),
                  ("PF", 1)])

    ThinkRate = 5946.34
    TxRate = 763.80
    pn.add_imme_trans("Ri", guard=one_moref("Rall"),
                      in_arc=["PF"],
                      out_arc=["Done"])
    pn.add_exp_trans("PP0th", ThinkRate, in_arc=["Start"], out_arc=["PP"])
    pn.add_exp_trans("PP0tx", TxRate, in_arc=["PP"], out_arc=["P1","P2","P3"])
    pn.add_exp_trans("P1th", ThinkRate, in_arc=["P1"], out_arc=["P1p"])
    pn.add_exp_trans("P2th", ThinkRate, in_arc=["P2"], out_arc=["P2p"])
    pn.add_exp_trans("P3th", ThinkRate, in_arc=["P3"], out_arc=["P3p"])
    pn.add_exp_trans("P1tx", TxRate, in_arc=["P1p"], out_arc=["C0", "C2", "C3"])
    pn.add_exp_trans("P2tx", TxRate, in_arc=["P2p"], out_arc=["C0", "C1", "C3"])
    pn.add_exp_trans("P3tx", TxRate, in_arc=["P3p"], out_arc=["C0", "C1", "C2"])
    pn.add_exp_trans("C0th", ThinkRate, in_arc=["PC0"], out_arc=["C0p"], guard=two_timesf("C0"))
    pn.add_exp_trans("C1th", ThinkRate, in_arc=["PC1"], out_arc=["C1p"], guard=two_timesf("C1"))
    pn.add_exp_trans("C2th", ThinkRate, in_arc=["PC2"],out_arc=["C2p"], guard=two_timesf("C2"))
    pn.add_exp_trans("C3th", ThinkRate, in_arc=["PC3"],out_arc=["C3p"], guard=two_timesf("C3"))
    pn.add_exp_trans("C0tx", TxRate, in_arc=["C0p"], out_arc=["R1", "R2", "R3"])
    pn.add_exp_trans("C1tx", TxRate, in_arc=["C1p"], out_arc=["R0", "R2", "R3"])
    pn.add_exp_trans("C2tx", TxRate, in_arc=["C2p"], out_arc=["R0", "R1", "R3"])
    pn.add_exp_trans("C3tx", TxRate, in_arc=["C3p"], out_arc=["R0", "R1", "R2"])
    pn.add_imme_trans("R0th", in_arc=["PR1"],out_arc=["Rall"], guard=two_timesf("R0"))
    pn.add_imme_trans("R1th", in_arc=["PR2"],out_arc=["Rall"], guard=two_timesf("R1"))
    pn.add_imme_trans("R2th", in_arc=["PR3"],out_arc=["Rall"], guard=two_timesf("R2"))
    pn.add_imme_trans("R3th", in_arc=["PR4"],out_arc=["Rall"], guard=two_timesf("R3"))
    pn.set_halt_condition(lambda x: True if x.token("Done") != 0 else False)
    place_of_interest = ["C0", "C1", "C2", "C3", "R0", "R1", "R2", "R3", "Rall"]
    for p in place_of_interest:
        pn.add_inst_reward_func(p, place_token(p))
    pn.add_cum_reward_func("mtta", lambda x: 0 if x.is_absorbing() else 1)
    pn.solve()
    for p in place_of_interest:
        print("Token in ", p, " is:", pn.get_inst_reward(p))
    print("mtta:", pn.get_cum_reward("mtta"))
    pn.dispose()

test_blockchain_pn()
