import model
import display
def draw():
    pn = model.PetriNet()
    pn.config_logger("test_logger.conf")
    def less_than_five(x):
        return x.token("createPred") < 5
    pn.add_imme_trans("start", guard=less_than_five, out_arc=["createPred"]);
    display.show_petri_net(pn, interactive=True)
    #pn.solve()
draw()
