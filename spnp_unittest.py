import unittest
from petri_net_set import pn_creator_func
import os


class TestMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists("test_fig"):
            os.makedirs("test_fig")

    def setUp(self):
        self.petri_nets = []
        for name, func in pn_creator_func:
            self.petri_nets.append((name, func()))

    def tearDown(self):
        for name, pn in self.petri_nets:
            pn.dispose()

    def test_default_solve(self):
        for name, pn in self.petri_nets:
            print("solving with default method:", name)
            pn.solve()
            for name, val in pn.get_rewards():
                print(name, ":", val)

    def test_draw(self):
        for name, pn in self.petri_nets:
            print("drawing:", name)
            G = pn.to_agraph()
            G.layout(prog="dot")
            G.draw("test_fig/" + name + ".svg")

    def test_draw_marking_chain(self):
        for name, pn in self.petri_nets:
            print("drawing marking chain:", name)
            G = pn.to_marking_chain_agraph()
            G.layout(prog="dot")
            G.draw("test_fig/" + name + "_chain.svg")

if __name__ == '__main__':
    unittest.main()
