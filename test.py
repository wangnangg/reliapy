from spnp import *
def guard_func(context):
    return True

def param_func(context):
    print("param call back")
    return 3.14
def var_multi(context):
    print("multi call back")
    return 2
def test1():
    pn = PetriNet()
    pn.add_place("p1")
    pn.add_place("p2")
    pn.add_imme_trans("t1", param_func, guard=guard_func, in_arc=[("p1", var_multi)], out_arc=[("p2", 1)])
    pn.add_exp_trans("t2", 1.0, in_arc=[("p2", 1)], out_arc=[("p1", 1)], priority=1)

def reward(context):
    return context.token("p1")

def mtta_func(x):
    if x.is_absorbing():
        return 0
    else:
        return 1

def test2():
    pn = PetriNet()
    pn.add_place([("p1",1), "p2"])
    pn.add_exp_trans("t1", 0.001,
                     in_arc=["p1"],
                     out_arc=["p2"])
    pn.add_exp_trans("t2", 0.2,
                     in_arc=["p2"],
                     out_arc=["p1"])
    pn.add_inst_reward_func("up",lambda x : x.token("p1"))
    pn.add_cum_reward_func("mtta", mtta_func)
    pn.solve()
    print(pn.get_inst_reward("up"))

    pn.add_inst_reward_func("down",lambda x : x.token("p2"))
    pn.set_option(steady_state_method="power")
    pn.solve()
    print("up:", pn.get_inst_reward("up"))
    print("down:", pn.get_inst_reward("down"))
    print("mtta:", pn.get_cum_reward("mtta"))
    pn.dispose()

def test3():
    pn = PetriNet()
    pn.add_place([("p1",1),"p2", "p3"])
    pn.add_exp_trans("t1", 0.1,
                     in_arc=["p1"],
                     out_arc=["p2"])
    pn.add_exp_trans("t2", 1.0,
                     in_arc=["p2"],
                     out_arc=["p1"])
    pn.add_exp_trans("t3", 0.2,
                     in_arc=["p2"],
                     out_arc=["p3"])
    pn.add_inst_reward_func("all", lambda x: x.token("p3"))
    pn.add_cum_reward_func("mtta", mtta_func)
    pn.set_option(steady_state_method="power")
    pn.solve()
    print(pn.get_inst_reward("all"))
    print("mtta:", pn.get_cum_reward("mtta"))
    pn.set_option(steady_state_method="sor")
    pn.solve()
    print(pn.get_inst_reward("all"))
    print("mtta:", pn.get_cum_reward("mtta"))
    pn.dispose()

def test4():
    pn = PetriNet()
    pn.add_place("p1")
    pn.add_place("p2")
    pn.add_place("p3")
    pn.add_exp_trans("t1", 0.1, in_arc=["p1"], out_arc=["p2"])
    pn.add_exp_trans("t2", 0.2, in_arc=["p2"], out_arc=["p3"])
    pn.set_init_token("p1", 1)
    pn.add_cum_reward_func("mtta", mtta_func)
    pn.solve()
    print("simple mtta:", pn.get_cum_reward("mtta"))

def test_molloys():
    pn = PetriNet()
    for i in range(5):
        pn.add_place("p"+str(i))
    pn.add_exp_trans("t0", 1.0, in_arc=[("p0", 1)],
                     out_arc=[("p1", 1),
                              ("p2", 1)])

test2()
test3()
test4()
