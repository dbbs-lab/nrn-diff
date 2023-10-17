import unittest
from nrndiff import nrn_diff
from neuron import h


class TestTypeDiff(unittest.TestCase):
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


class TestSectionDiff(unittest.TestCase):
    def test_section_default_equal(self):
        a = h.Section()
        b = h.Section()
        diff = nrn_diff(a, b)
        self.assertEqual(0, len(diff), f"Default sections should be identical")

    def test_section_attr_diff(self):
        for attr in ("L", "diam", "Ra", "cm", "nseg", "v"):
            with self.subTest(attr=attr):
                a = h.Section()
                b = h.Section()
                # Change value of one section and repeat diff
                v = getattr(a, attr)
                setattr(b, attr, v**2 + v + 10)
                diff = nrn_diff(a, b)
                # Filter out underlying differences that stem from the attr difference
                diff = [d for d in diff if d.differ.parent is None]
                self.assertEqual(
                    1, len(diff), f"Modified {attr} should not be identical"
                )

    def test_section_point_diff(self):
        a = h.Section()
        b = h.Section()
        a.pt3dadd(0, 0, 0, 0)
        diff = nrn_diff(a, b)
        self.assertEqual(
            1,
            len([d for d in diff if d.name == "SectionPointDifference"]),
            f"Point difference expected",
        )
        b.pt3dadd(0, 0, 0, 0)
        diff = nrn_diff(a, b)
        self.assertEqual(0, len(diff), f"Difference equalized")
        b.pt3dadd(0, 0, 0, 0)
        diff = nrn_diff(a, b)
        self.assertEqual(1, len(diff), f"Shape point difference expected")
        a.pt3dadd(0, 0, 0, 0.1)
        diff = nrn_diff(a, b)
        self.assertEqual(1, len(diff), f"diam point difference expected")
