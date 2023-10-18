import unittest
from nrndiff import nrn_diff
from nrndiff import _differences
from neuron import h


class TestTypeDiff(unittest.TestCase):
    def test_no_type_diff_with_primitives(self):
        diff = nrn_diff(5, 5)
        self.assertEqual(0, len(diff), "No type diff expected between int")

    def test_type_diff_with_primitives(self):
        class hashlist(list):
            def __hash__(self):
                return id(self)

        diff = nrn_diff(5, hashlist())
        self.assertEqual(1, len(diff), "Type diff expected between int and list")
        typediff = diff[0]
        self.assertIsInstance(typediff, _differences.TypeDifference)

    def test_typeid_diff_with_primitives(self):
        diff = nrn_diff(5, True)
        self.assertEqual(1, len(diff), "Type diff expected between int and bool")
        typediff = diff[0]
        self.assertIsInstance(
            typediff,
            _differences.TypeIdentityDifference,
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
            len(
                [d for d in diff if isinstance(d, _differences.SectionPointDifference)]
            ),
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


class TestSegmentDiff(unittest.TestCase):
    def test_segment_nodiff(self):
        s = h.Section()
        a = s(0.5)
        b = s(0.5)
        diff = nrn_diff(a, b)
        self.assertEqual(0, len(diff), f"no difference expected")

    def test_segment_nosecdiff(self):
        s1 = h.Section()
        s2 = h.Section()
        a = s1(0.5)
        b = s2(0.5)
        diff = nrn_diff(a, b)
        self.assertEqual(0, len(diff), f"no difference expected")

    def test_segment_x_diff(self):
        s = h.Section()
        a = s(0.5)
        b = s(0.7)
        diff = nrn_diff(a, b)
        self.assertEqual(1, len(diff), f"x difference expected")
        self.assertIsInstance(diff[0], _differences.SegmentXDifference)

    def test_segment_attr_diff(self):
        sizediff = {
            _differences.SegmentAreaDifference,
            _differences.SegmentVolumeDifference,
            _differences.SegmentInputResistanceDifference,
        }
        irdiff = {_differences.SegmentInputResistanceDifference}
        vdiff = {_differences.SegmentPotentialDifference}
        for (attr, expected) in (
            ("L", sizediff),
            ("diam", sizediff),
            ("nseg", sizediff),
            ("Ra", irdiff),
            ("cm", set()),
            ("v", vdiff),
        ):
            with self.subTest(attr=attr):
                a = h.Section()
                b = h.Section()
                # Change value of one section and repeat diff
                v = getattr(a, attr)
                setattr(b, attr, v**2 + v + 10)
                diff = nrn_diff(a(0.5), b(0.5))
                # Filter out diffs that we find as seg's parent sec diffs
                diff = [d for d in diff if d.differ.parent is None]
                self.assertEqual(
                    expected,
                    set(type(d) for d in diff),
                    f"Modifying {attr} should give {expected}",
                )

    def test_segment_mech_diff(self):
        a = h.Section()
        a.insert("pas")
        b = h.Section()
        diff = nrn_diff(a, b)
        self.assertIsInstance(
            diff[0], _differences.SegmentMechanismDifference, "mechdiff expected"
        )
        b.insert("pas")
        diff = nrn_diff(a, b)
        self.assertEqual(0, len(diff), "no diff expected")


class TestMechanismDiff(unittest.TestCase):
    def test_mech_nodiff(self):
        a = h.Section()
        b = h.Section()
        a.insert("pas")
        b.insert("pas")

        diff = nrn_diff(a(0.5).pas, b(0.5).pas)
        self.assertEqual(0, len(diff), "no diff expected")

    def test_mech_sourcediff(self):
        a = h.Section()
        b = h.Section()
        a.insert("pas")
        b.insert("hh")

        diff = nrn_diff(a(0.5).pas, b(0.5).hh)
        self.assertEqual(1, len(diff), "source diff expected")
        self.assertIsInstance(diff[0], _differences.SourceDifference)


class TestParamDiff(unittest.TestCase):
    def test_param_nodiff(self):
        a = h.Section()
        b = h.Section()
        a.insert("pas")
        b.insert("pas")
        ag = next(iter(a(0.5).pas))
        bg = next(iter(b(0.5).pas))

        diff = nrn_diff(ag, bg)
        self.assertEqual(0, len(diff), "no diff expected")

    def test_param_diff(self):
        a = h.Section()
        b = h.Section()
        a.insert("pas")
        b.insert("pas")
        b.g_pas = b.g_pas**2 + b.g_pas + 10
        ag = next(iter(a(0.5).pas))
        bg = next(iter(b(0.5).pas))

        diff = nrn_diff(ag, bg)
        self.assertEqual(1, len(diff), "diff expected")
        self.assertIsInstance(diff[0], _differences.ParameterDifference)
