import unittest

from neuron import h

from nrndiff import get_differ_for


class TestMemo(unittest.TestCase):
    def test_segment_memo(self):
        s = h.Section()
        s.insert("pas")
        seg = s(0.5)
        differ = get_differ_for(seg)(seg, seg, None)
        memo = set()
        children = differ.get_children(memo)
        self.assertEqual(2, len(children), "should find sec&pas child in seg")
        self.assertEqual(2, len(memo), "should store sec&pas in memo")
        children = differ.get_children(memo)
        self.assertEqual(0, len(children), "should not find new children")
        self.assertEqual(2, len(memo), "should preserve memo")
