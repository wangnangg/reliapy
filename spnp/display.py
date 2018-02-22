from model import PetriNet
import export
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.collections as collection
import matplotlib.patches as pat
import matplotlib.lines as lines
import numpy as np

g_ax = None
g_cf = None
g_place_r = 20.0
g_imme_w = 40.0
g_imme_h = 2.0
g_exp_w = 40.0
g_exp_h = 16.0
g_arrow_head_size = 10.0
g_arrow_opt = {'head_width': g_arrow_head_size,
               'head_length': g_arrow_head_size,
               'length_includes_head': True}
g_enabled_color = 'r'
g_enabled_alpha = 0.5
g_enabled_imme_scale = 1.5
g_linewith = 1.0
g_fontsize = 12
g_default_color = 'black'

def show_petri_net(petri_net, marking=None, *, with_marking=True, interactive=True, with_label=True):
    plt.close()
    if with_marking:
        if marking:
            m = marking
        else:
            m = petri_net.get_init_marking()
    else:
        m = None
    draw_petri_net(petri_net, m, interactive=interactive, with_label=with_label)
    plt.show()

def draw_petri_net(petri_net, marking=None, *, interactive=True, with_label=True, layout_prog='dot', ax=None):
    global g_ax, g_cf
    G = export.petri_net_to_nxgraph(petri_net)
    pygraphviz_layout(G, with_label)
    if ax is None:
        cf = plt.gcf()
    else:
        cf = ax.get_figure()
    cf.set_facecolor('w')
    if ax is None:
        if cf._axstack() is None:
            ax = cf.add_axes((0, 0, 1, 1))
        else:
            ax = cf.gca()
    g_ax = ax
    g_cf = cf
    g_ax.axis('off')
    g_ax.spnp_data = {'ma_list': [], 'ta_list':[], 'petri_net':petri_net, 'nxgraph':G}
    __draw_pn_graph(G, petri_net, with_label)
    if marking:
        g_ax.spnp_data['marking'] = marking
        __redraw_marking(G, marking)

    if marking and interactive:
        g_cf.canvas.mpl_connect("pick_event", __onclick_transition)
        trans_status_map = {}
        for tname in petri_net.trans_map.keys():
            trans_status_map[tname] = petri_net.is_trans_enabled(tname, marking)
        __redraw_trans_status(G, trans_status_map)


def pygraphviz_layout(G,with_label, prog='dot'):
    import pygraphviz
    import re
    A=nx.nx_agraph.to_agraph(G)
    node_height = g_place_r * 2
    node_width = g_place_r * 2
    num_nodes = A.number_of_nodes()
    for n in A.nodes_iter():
        name_len = len(n.name)
        label_size = name_len * g_fontsize if with_label else 0
        n.attr["height"] = node_height / 72.0
        n.attr["width"] = node_width / 72.0
        n.attr["label_size"] = label_size
    A.layout(prog=prog)
    for n,d in G.nodes_iter(data=True):
        node=pygraphviz.Node(A,n)
        xx,yy=node.attr["pos"].split(',')
        xx, yy = float(xx), float(yy)
        lsize = float(node.attr["label_size"])
        x_node = xx
        x_label = xx - (lsize + node_width) / 2.0
        d["pos"]=(x_node,yy)
        d["label_pos"] = (x_label, yy)
    for u,v in G.edges_iter():
        e = A.get_edge(u, v)
        edge_pos_str = re.split("[, ]+", e.attr["pos"])[1:]
        edge_pos = list(map(lambda x : float(x), edge_pos_str))
        edge_ctrl_p = []
        for i in range(1, int(len(edge_pos) / 2)):
            edge_ctrl_p.append((edge_pos[i*2], edge_pos[i*2+1]))
        edge_ctrl_p.append((edge_pos[0], edge_pos[1]))
        G[u][v]["pos"] = edge_ctrl_p

def __onclick_transition(event):
    tname = event.artist.spnp_data['name']
    pn = g_ax.spnp_data['petri_net']
    marking = g_ax.spnp_data['marking']
    G = g_ax.spnp_data['nxgraph']
    next_marking = pn.fire(tname, marking)
    __redraw_marking(G, next_marking)
    trans_status_map = {}
    for tname in pn.trans_map.keys():
        trans_status_map[tname] = pn.is_trans_enabled(tname, next_marking)
    __redraw_trans_status(G, trans_status_map)
    event.canvas.draw()

def __redraw_trans_status(G, status_map):
    ta_list = g_ax.spnp_data['ta_list']
    for a in ta_list:
        a.remove()
    ta_list = []
    for n, d in G.nodes_iter(data=True):
        typ = d['type']
        if typ == 'imme' and status_map[n]:
            if status_map[n]:
                x, y = d['pos']
                w, h = g_imme_w * g_enabled_imme_scale, g_imme_h * g_enabled_imme_scale * 2
                c = pat.Rectangle( (x - w / 2.0, y - h / 2.0), w, h, fill=True, fc=g_enabled_color, edgecolor=g_enabled_color, alpha  = g_enabled_alpha)
                g_ax.add_patch(c)
                ta_list.append(c)
        elif typ == 'exp' and status_map[n]:
                x, y = d['pos']
                c = pat.Rectangle( (x - g_exp_w / 2.0, y - g_exp_h / 2.0), g_exp_w, g_exp_h, fill=True, fc=g_enabled_color, alpha = g_enabled_alpha)
                g_ax.add_patch(c)
                ta_list.append(c)
    g_ax.spnp_data['ta_list'] = ta_list

def __redraw_marking(G, marking):
    ma_list = g_ax.spnp_data['ma_list']
    for a in ma_list:
        a.remove()
    ma_list = []
    for n, d in G.nodes_iter(data=True):
        typ = d['type']
        if typ == 'place':
            pos = d['pos']
            num = marking[n]
            ma_list.append(__draw_token(pos, num))
    g_ax.spnp_data['ma_list'] = ma_list
    g_ax.spnp_data['marking'] = marking

def __draw_pn_graph(G, petri_net, with_label):
    with plt.style.context({'lines.linewidth':g_linewith,
                            'lines.color':g_default_color,
                            'patch.linewidth':g_linewith,
                            'patch.facecolor':g_default_color,
                            'patch.edgecolor':g_default_color,
                            'font.size' : g_fontsize}):
        for n, d in G.nodes_iter(data=True):
            typ = d["type"]
            pos = d["pos"]
            label_pos = d["label_pos"]
            if typ == "place":
                __draw_place(pos)
            elif typ == "imme":
                __draw_imme_trans(pos, petri_net, n)
            elif typ == "exp":
                __draw_exp_trans(pos, petri_net, n)
            if with_label:
                __draw_label(label_pos, n)
        for src, dest, data in G.edges_iter(data=True):
            typ = data["type"]
            src_pos = G.node[src]["pos"]
            dest_pos = G.node[dest]["pos"]
            edge_points = G.edge[src][dest]["pos"]
            if typ == "in_arc":
                __draw_in_arc(src_pos, dest_pos, edge_points,  G.node[dest]["type"])
            elif typ == "out_arc":
                __draw_out_arc(src_pos, dest_pos, edge_points, G.node[src]["type"])
            elif typ == "inh_arc":
                __draw_inh_arc(src_pos, dest_pos, edge_points, G.node[dest]["type"])
        g_ax.set_aspect(1)
        g_ax.relim()
        g_ax.autoscale()


def __draw_place(center):
    c = pat.Circle(center, g_place_r, fill=False)
    g_ax.add_patch(c)

def __draw_text(center, txt):
    return g_ax.text(*center, txt,
            horizontalalignment='center',
            verticalalignment='center', color='black')

def __draw_label(center, txt):
    __draw_text(center, txt)

def __draw_token(center, num):
    return __draw_text(center, str(num))

def __draw_imme_trans(center, petri_net, trans_name):
    x, y = center
    c = pat.Rectangle( (x - g_imme_w / 2.0, y - g_imme_h / 2.0), g_imme_w, g_imme_h, fill=True, edgecolor=g_default_color, picker=10)
    c.spnp_data = {'type':'imme', 'name':trans_name}
    g_ax.add_patch(c)

def __draw_exp_trans(center, petri_net, trans_name):
    x, y = center
    c = pat.Rectangle( (x - g_exp_w / 2.0, y - g_exp_h / 2.0), g_exp_w, g_exp_h, fill=False, picker=True)
    c.spnp_data = {'type':'exp', 'name':trans_name}
    g_ax.add_patch(c)

def __diff(org, point):
    return point[0] - org[0], point[1] - org[1]

def __diff_norm(org, point):
    return __norm(*__diff(org, point))

def __scale_point(org, point, scale):
    dx, dy = __diff(org, point)
    dx *= scale
    dy *= scale
    return org[0] + dx, org[1] + dy

def __extend_point(org, point, size):
    dx, dy = __diff(org, point)
    scale = 1 + size / np.sqrt(dx * dx + dy * dy)
    return __scale_point(org, point, scale)

def __norm(x , y):
    return np.sqrt(x*x + y*y)

def __rotation_matrix(r):
    sr = np.sin(r)
    cr = np.cos(r)
    return [[cr, -sr], [sr, cr]]

def __rotate_point(org, point, degree):
    radius = np.deg2rad(degree)
    rm = __rotation_matrix(radius)
    dx, dy = __diff(org, point)
    dxy = np.dot(rm, [dx, dy])
    return org[0] + dxy[0], org[1] + dxy[1]

def __draw_in_arc(src, dest, edge_points, trans_type):
    if trans_type == "imme":
        tw = g_imme_w
        th = g_imme_h
        tr = th / tw
    elif trans_type == "exp":
        tw = g_exp_w
        th = g_exp_h
        tr = th / tw
    src_shrink_size = -g_place_r
    dx, dy = __diff(edge_points[-1], dest)
    if dx == 0.0 or np.abs(dy / dx) > tr:
        dest_shrink_size = -__norm(th / 2, th / 2 * np.abs(dx / dy))
    else:
        dest_shrink_size = -__norm(tw / 2, tw / 2 * np.abs(dy / dx))
    __draw_path(src, dest,edge_points, src_shrink_size, dest_shrink_size, head='triangle')

def __draw_out_arc(src, dest, edge_points, trans_type):
    if trans_type == "imme":
        tw = g_imme_w
        th = g_imme_h
        tr = th / tw
    elif trans_type == "exp":
        tw = g_exp_w
        th = g_exp_h
        tr = th / tw
    dest_shrink_size = -g_place_r
    dx, dy = __diff(src, edge_points[0])
    if dx == 0.0 or np.abs(dy / dx) > tr:
        src_shrink_size = -__norm(th / 2, th / 2 * np.abs(dx / dy))
    else:
        src_shrink_size = -__norm(tw / 2, tw / 2 * np.abs(dy / dx))
    __draw_path(src, dest, edge_points, src_shrink_size, dest_shrink_size, head='triangle')

def __draw_inh_arc(src, dest, edge_points, trans_type):
    if trans_type == "imme":
        tw = g_imme_w
        th = g_imme_h
        tr = th / tw
    elif trans_type == "exp":
        tw = g_exp_w
        th = g_exp_h
        tr = th / tw
    src_shrink_size = -g_place_r
    dx, dy = __diff(edge_points[-1], dest)
    if dx == 0.0 or np.abs(dy / dx) > tr:
        dest_shrink_size = -__norm(th / 2, th / 2 * np.abs(dx / dy))
    else:
        dest_shrink_size = -__norm(tw / 2, tw / 2 * np.abs(dy / dx))
    __draw_path(src, dest, edge_points, src_shrink_size, dest_shrink_size, head='circle')

def __center(p1, p2):
    return (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0

def __draw_path(src, dest, ctrl_points, src_extend_size, dest_extend_size, head):
    src_next = ctrl_points[0]
    src = __extend_point(src_next, src, src_extend_size)
    dest_last = ctrl_points[-1]
    head_end = __extend_point(dest_last, dest, dest_extend_size)
    dest = __extend_point(dest_last, dest, dest_extend_size - g_arrow_head_size)
    cxs, cys = zip(*ctrl_points)
    xs = [src[0]]
    xs.extend(cxs)
    xs.append(dest[0])
    ys = [src[1]]
    ys.extend(cys)
    ys.append(dest[1])
    l = lines.Line2D(xs, ys)
    g_ax.add_line(l)
    __draw_head(dest, head_end, head)


def __draw_head(start, end, head):
    if head == "circle":
        c = pat.Circle(__center(start, end), radius=g_arrow_head_size / 2, fill=False)
        g_ax.add_patch(c)
    elif head == "triangle":
        p1 = end
        size = __diff_norm(start, end)
        p_ref = __extend_point(start, end, -size / np.cos(np.deg2rad(30)))
        p2 = __rotate_point(end, p_ref, 30)
        p3 = __rotate_point(end, p_ref, -30)
        tri = pat.Polygon([p1, p2, p3])
        g_ax.add_patch(tri)
