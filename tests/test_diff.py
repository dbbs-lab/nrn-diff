import unittest
from nrndiff import nrn_diff
from neuron import h


class TestDiff(unittest.TestCase):
    def test_no_type_diff_with_primitives(self):
        diff = nrn_diff(5, 5)
        self.assertEqual(0, len(diff), "No type diff expected between int")

    def test_type_diff_with_primitives(self):
        diff = nrn_diff(5, [])
        self.assertEqual(1, len(diff), "Type diff expected between int and list")
        typediff = diff[0]
        self.assertEqual("TypeDifference", typediff.name)

    def test_typeid_diff_with_primitives(self):
        diff = nrn_diff(5, True)
        self.assertEqual(1, len(diff), "Type diff expected between int and bool")
        typediff = diff[0]
        self.assertEqual(
            "TypeIdentityDifference",
            typediff.name,
            "int and bool should have child-parent relationship",
        )

    def test_section_length_diff(self):
        a = h.Section()
        b = h.Section()
        diff = nrn_diff(a, b)
        self.assertEqual(0, len(diff), "Default sections should be identical")
        # Change length of one section and repeat diff
        b.L = a.L**2 + a.L + 10
        diff = nrn_diff(a, b)
        self.assertEqual(1, len(diff), "Modified length should not be identical")

    def test_section_diam_diff(self):
        a = h.Section()
        b = h.Section()
        diff = nrn_diff(a, b)
        self.assertEqual(0, len(diff), "Default sections should be identical")
        # Change length of one section and repeat diff
        b.diam = a.diam**2 + a.diam + 10
        diff = nrn_diff(a, b)
        self.assertEqual(1, len(diff), "Modified length should not be identical")
