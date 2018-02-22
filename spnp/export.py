from model import PetriNet
import reliapy
import json
import pygraphviz as pyg
import networkx as nx



def petri_net_to_agraph(pn : PetriNet):
    j = json.loads(reliapy.export_petri_net(pn.pn_ptr))
    g = pyg.AGraph(strict=True, directed=True)
    for name, index in pn.place_map.items():
        g.add_node(name, type="place")
    for name, index in pn.trans_map.items():
        g.add_node(name)
        trans = j["transition"]
        in_arc = trans[index].pop("in_arc")
        out_arc = trans[index].pop("out_arc")
        inh_arc = trans[index].pop("inh_arc")
        g.get_node(name).attr.update(trans[index])
        for arc in in_arc:
            pname = pn.place_rev_map[arc["p_index"]]
            g.add_edge(pname, name, type="in_arc", multi=arc["multi"])
        for arc in out_arc:
            pname = pn.place_rev_map[arc["p_index"]]
            g.add_edge(name, pname, type="out_arc", multi=arc["multi"])
        for arc in inh_arc:
            pname = pn.place_rev_map[arc["p_index"]]
            g.add_edge(pname, name, type="inh_arc", multi=arc["multi"])
    return g

def petri_net_to_reachability_agraph(pn: PetriNet):
    G = pyg.AGraph(strict=True, directed=True)
    png = reliapy.export_marking_chain(pn.pn_ptr)
    for node in png.node_list:
        G.add_node(node.index)
    for edge in png.edge_list:
        G.add_edge(edge.src, edge.dest, rate=edge.param)
    return G


def petri_net_to_nxgraph(pn : PetriNet):
    j = json.loads(reliapy.export_petri_net(pn.pn_ptr))
    g = nx.DiGraph()
    for name, index in pn.place_map.items():
        g.add_node(name, type="place")
    for name, index in pn.trans_map.items():
        g.add_node(name)
        trans = j["transition"]
        in_arc = trans[index].pop("in_arc")
        out_arc = trans[index].pop("out_arc")
        inh_arc = trans[index].pop("inh_arc")
        g.node[name].update(trans[index])
        for arc in in_arc:
            pname = pn.place_rev_map[arc["p_index"]]
            g.add_edge(pname, name, type="in_arc", multi=arc["multi"])
        for arc in out_arc:
            pname = pn.place_rev_map[arc["p_index"]]
            g.add_edge(name, pname, type="out_arc", multi=arc["multi"])
        for arc in inh_arc:
            pname = pn.place_rev_map[arc["p_index"]]
            g.add_edge(pname, name, type="inh_arc", multi=arc["multi"])
    return g

