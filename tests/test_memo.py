import unittest

from neuron import h, nrn

from nrndiff import get_differ_for
from nrndiff._util import Memo


def _memo_step(memo, children):
    ret = []
    for child_pair in children:
        if isinstance(child_pair, tuple):
            left, right = child_pair
        else:
            left = right = child_pair
        ichildren = memo.visit(get_differ_for(left)(left, right, None).get_children())
        ret.extend(ichildren)
    return ret


class TestMemo(unittest.TestCase):
    def test_segment_memo(self):
        s = h.Section()
        s.insert("pas")
        seg = s(0.5)
        differ = get_differ_for(seg)(seg, seg, None)
        memo = Memo({seg})
        children = [*memo.visit(differ.get_children())]
        self.assertEqual(2, len(children), "should find sec&pas child in seg")
        self.assertEqual(3, len(memo), "should store sec&pas in memo")
        children = [*memo.visit(differ.get_children())]
        self.assertEqual(0, len(children), "should not find new children")
        self.assertEqual(3, len(memo), "should preserve memo")

    def test_mech_memo(self):
        s = h.Section()
        s.insert("pas")
        mech = s(0.5).pas
        memo = Memo({mech})
        children = _memo_step(memo, [mech])
        self.assertEqual(4, len(children), "1 parent seg + 3 params")
        self.assertEqual(5, len(memo), "1 parent seg + 3 params")
        seg = [c[0] for c in children if isinstance(c[0], nrn.Segment)]
        self.assertEqual(1, len(seg), "mech should have 1 parent seg")
        self.assertIn(seg[0], memo, "seg should be in memo")
        rangevars = [c[0] for c in children if isinstance(c[0], nrn.RangeVar)]
        self.assertEqual(1, len(seg), "pas should have g, e, i params")
        for rv in rangevars:
            with self.subTest(param=rv.name()):
                self.assertIn(rv, memo, f"{rv.name()} should be in memo")
        sec = _memo_step(memo, children)
        self.assertEqual(1, len(sec), "expected 1 grandchild")
        self.assertIsInstance(sec[0][0], nrn.Section, "expected section grandchild")
        self.assertIn(sec[0][0], memo, "sec should be in memo")
        remainder = _memo_step(memo, sec)
        self.assertEqual([], remainder, "no more nodes to visit")

    def test_param_memo(self):
        a = h.Section()
        b = h.Section()
        a.insert("pas")
        b.insert("pas")
        ag = next(iter(a(0.5).pas))
        bg = next(iter(b(0.5).pas))
