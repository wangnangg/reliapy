#!/usr/bin/python3
import reliapy

class PetriNet:
    def __init__(self):
        self.pn_ptr = reliapy.create_petri_net(self.__wrap_context)
        self.place_map = {}
        self.trans_map = {}
        self.reward_map = {}
        self.place_count = 0
    def dispose(self):
        reliapy.delete_petri_net(self.pn_ptr)
    def __wrap_context(self, __context):
        return PetriNetState(__context, self.place_map, self.trans_map)

    def add_place(self, name):
        self.place_map[name] = self.place_count
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
        param_val = 1.0
        param_func = None
        if callable(param):
            param_func = param
        else:
            param_val = param
        trans_index = reliapy.add_transition(self.pn_ptr, trans_type, guard, param_val, param_func, priority)
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

    def add_imme_trans(self, name, prob, *, priority=0, guard=None, in_arc=[], out_arc=[], inh_arc=[]):
        self.__add_trans(0, name, prob, priority, guard, in_arc, out_arc, inh_arc)

    def add_exp_trans(self, name, prob, *, priority=0, guard=None, in_arc=[], out_arc=[], inh_arc=[]):
        self.__add_trans(1, name, prob, priority, guard, in_arc, out_arc, inh_arc)

    def set_init_token(self, place_name, token_num):
        place_index = self.place_map[place_name]
        reliapy.set_init_token(self.pn_ptr, place_index, token_num)

    def add_inst_reward_func(self, name, reward_func):
        index = reliapy.add_inst_reward(self.pn_ptr, reward_func)
        self.reward_map[name] = index

    def get_inst_reward(self, name):
        index = self.reward_map[name]
        return reliapy.get_inst_reward(self.pn_ptr, index)

    def solve(self):
        result = reliapy.solve_steady_state(self.pn_ptr)
        return result




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
