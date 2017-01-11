#!/usr/bin/python3
import reliapy
import math

class PetriNet:
    ss_method = ["auto", "sor", "power", "divide"]
    ts_method = ["auto"]

    def __init__(self):
        self.pn_ptr = reliapy.create_petri_net(self.__wrap_context)
        self.place_map = {}
        self.place_rev_map = {}
        self.trans_map = {}
        self.trans_rev_map = {}
        self.inst_reward_map = {}
        self.cum_reward_map = {}
        self.place_count = 0

    def dispose(self):
        reliapy.delete_petri_net(self.pn_ptr)

    def __wrap_context(self, __context):
        return PetriNetState(__context, self.place_map, self.trans_map)

    def set_option(self, *, steady_state_method=None,
                   transient_state_method=None,
                   max_iteration=None,
                   precision=None,
                   sor_omega=None
                   ):
        if steady_state_method:
            try:
                index = PetriNet.ss_method.index(steady_state_method)
            except:
                raise Exception("Unknown steady state method. Candidates are: " + str(PetriNet.ss_method))
            reliapy.option_set_ss_method(self.pn_ptr, index)
        if transient_state_method:
            try:
                index = PetriNet.ts_method.index(transient_state_method)
            except:
                raise Exception("Unknown steady state method. Candidates care: " + str(PetriNet.ts_method))
            reliapy.option_set_ts_method(self.pn_ptr, index)
        if max_iteration:
            reliapy.option_set_max_iter(self.pn_ptr, max_iteration)
        if precision:
            reliapy.option_set_precision(self.pn_ptr, precision)
        if sor_omega:
            reliapy.option_set_sor_omega(self.pn_ptr, sor_omega)

    def add_place(self, place):
        if not isinstance(place, list):
            place = [place]
        for pair in place:
            if isinstance(pair, tuple):
                name = pair[0]
                num = pair[1]
                index = self.place_count
                if name in self.place_map or name in self.trans_map:
                    raise KeyError("Duplicate name.")
                self.place_map[name] = index
                self.place_rev_map[index] = name
                self.place_count += 1
                reliapy.set_init_token(self.pn_ptr, index, num)
            else:
                if pair in self.place_map or pair in self.trans_map:
                    raise KeyError("Duplicate name.")
                self.place_map[pair] = self.place_count
                self.place_rev_map[self.place_count] = pair
                self.place_count += 1

    def __add_arc(self, arc_type, trans_index, place_name, multi):
        place_index = self.place_map[place_name]
        multi_val = 1
        multi_func = None
        if callable(multi):
            multi_func = multi
        else:
            multi_val = multi
        reliapy.add_arc(self.pn_ptr, arc_type, trans_index, place_index, multi_val, multi_func)

    def __add_trans(self, trans_type, name, param, priority, guard, in_arc, out_arc, inh_arc):
        if name in self.place_map or name in self.trans_map:
            raise KeyError("Duplicate name.")
        param_val = 1.0
        param_func = None
        if callable(param):
            param_func = param
        else:
            param_val = param
        trans_index = reliapy.add_transition(self.pn_ptr, trans_type, guard, param_val, param_func, priority)
        self.trans_map[name] = trans_index
        self.trans_rev_map[trans_index] = name
        for arc in in_arc:
            if not isinstance(arc, tuple):
                arc = (arc, 1)
            place_name, multi = arc
            self.__add_arc(0, trans_index, place_name, multi)
        for arc in out_arc:
            if not isinstance(arc, tuple):
                arc = (arc, 1)
            place_name, multi = arc
            self.__add_arc(1, trans_index, place_name, multi)
        for arc in inh_arc:
            if not isinstance(arc, tuple):
                arc = (arc, 1)
            place_name, multi = arc
            self.__add_arc(2, trans_index, place_name, multi)

    def add_imme_trans(self, name, prob=1.0, *, priority=0, guard=None, in_arc=[], out_arc=[], inh_arc=[]):
        self.__add_trans(0, name, prob, priority, guard, in_arc, out_arc, inh_arc)

    def add_exp_trans(self, name, prob, *, priority=0, guard=None, in_arc=[], out_arc=[], inh_arc=[]):
        self.__add_trans(1, name, prob, priority, guard, in_arc, out_arc, inh_arc)

    def set_init_token(self, place_name, token_num):
        place_index = self.place_map[place_name]
        reliapy.set_init_token(self.pn_ptr, place_index, token_num)

    def add_inst_reward_func(self, name, reward_func):
        index = reliapy.add_inst_reward(self.pn_ptr, reward_func)
        self.inst_reward_map[name] = index

    def get_inst_reward(self, name):
        index = self.inst_reward_map[name]
        return reliapy.get_inst_reward(self.pn_ptr, index)

    def add_cum_reward_func(self, name, reward_func):
        index = reliapy.add_cum_reward(self.pn_ptr, reward_func)
        self.cum_reward_map[name] = index

    def measure_place_nonempty_prob(self, name=None):
        if name:
            self.add_inst_reward_func(name +" nonempty prob", lambda x: 1 if x.token(name) > 0 else 0)
        else:
            for key in self.place_map:
                self.add_inst_reward_func(key + " nonempty prob", lambda x, key=key: 1 if x.token(key) > 0 else 0)
    def measure_MTTA(self):
        self.add_cum_reward_func("MTTA", lambda x: 0 if x.is_absorbing() else 1)

    def get_cum_reward(self, name):
        index = self.cum_reward_map[name]
        return reliapy.get_cum_reward(self.pn_ptr, index)

    def get_rewards(self):
        result = []
        for name, index in self.cum_reward_map.items():
            result.append((name, reliapy.get_cum_reward(self.pn_ptr, index)))
        for name, index in self.inst_reward_map.items():
            result.append((name, reliapy.get_inst_reward(self.pn_ptr, index)))
        return result

    def set_halt_condition(self, halt_func):
        reliapy.set_halt_condition(self.pn_ptr, halt_func)

    def solve(self):
        result = reliapy.solve_steady_state(self.pn_ptr)
        if not result:
            raise Exception("precision not reached.")

    def to_agraph(self):
        G = export_to_agraph(self)
        decorate_petri_net_agraph(G)
        return G

    def to_marking_chain_agraph(self):
        G = export_to_marking_chain_agraph(self)
        decorate_marking_chain_agraph(G)
        return G


class PetriNetState:
    def __init__(self, __context, place_map, trans_map):
        self.__context = __context
        self.place_map = place_map
        self.trans_map = trans_map

    def token(self, name):
        index = self.place_map[name]
        return reliapy.get_token_num(self.__context, index)

    def is_trans_enabled(self, name):
        index = self.trans_map[name]
        return reliapy.is_trans_enabled(self.__context, index)

    def has_enabled_trans(self):
        return reliapy.has_enbaled_trans(self.__context)

    def is_absorbing(self):
        return not reliapy.has_enbaled_trans(self.__context)


def export_to_agraph(pn: PetriNet):
    import pygraphviz as pgv
    G = pgv.AGraph(strict=True, directed=True)
    png = reliapy.export_petri_net(pn.pn_ptr)
    for node in png.node_list:
        if node.type == 0:  # place
            name = pn.place_rev_map[node.index]
            type = "place"
        elif node.type == 1:  # imme
            name = pn.trans_rev_map[node.index]
            type = "imme_trans"
        else:  # exp
            name = pn.trans_rev_map[node.index]
            type = "exp_trans"
        G.add_node(name, type=type, param=node.param)
    for edge in png.edge_list:
        multi = edge.param
        if edge.type == 0:  # in
            src = pn.place_rev_map[edge.src]
            dest = pn.trans_rev_map[edge.dest]
            type = "in"
        elif edge.type == 1:  # out
            dest = pn.place_rev_map[edge.dest]
            src = pn.trans_rev_map[edge.src]
            type = "out"
        else:  # inhibitor
            src = pn.place_rev_map[edge.src]
            dest = pn.trans_rev_map[edge.dest]
            type = "inhibitor"
        G.add_edge(src, dest, type=type, multi=multi)
    return G


# import pygraphviz as pgv
def decorate_petri_net_agraph(G):  # pgv.AGraph):
    for node in G.nodes():
        if node.attr["type"] == "place":
            shape = "circle"
        elif node.attr["type"] == "imme_trans":
            shape = "diamond"
            node.attr["label"] = ""
            node.attr["height"] = 0.02

        elif node.attr["type"] == "exp_trans":
            shape = "rect"
            node.attr["label"] = ""
            node.attr["height"] = 0.1
        else:
            raise AttributeError("Unkonwn node type.")
        node.attr["shape"] = shape
    for edge in G.edges():
        if edge.attr["type"] == "inhibitor":
            arrowhead = "odot"
        else:
            arrowhead = "normal"
        edge.attr["arrowhead"] = arrowhead
    return G

def export_to_marking_chain_agraph(pn: PetriNet):
    import pygraphviz as pgv
    G = pgv.AGraph(strict=True, directed=True)
    png = reliapy.export_marking_chain(pn.pn_ptr)
    for node in png.node_list:
        G.add_node(node.index)
    for edge in png.edge_list:
        G.add_edge(edge.src, edge.dest, rate=edge.param)
    return G

def decorate_marking_chain_agraph(G):
    #for edge in G.edges():
    #    edge.attr["label"] = edge.attr["rate"]
    return G
