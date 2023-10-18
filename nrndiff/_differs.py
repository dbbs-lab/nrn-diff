import abc as _abc
from . import _differences
from neuron import nrn as _nrn


def get_differ_for(nrnobj):
    t = type(nrnobj)
    return Differ._differs.get(t, None)


class Differ(_abc.ABC):
    _differs = {}

    def __init__(self, left, right, parent):
        self._left = left
        self._right = right
        self._parent = parent

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @property
    def parent(self):
        return self._parent

    def __init_subclass__(cls, difftype=None, **kwargs):
        if difftype is None:
            raise TypeError(
                "Differ child classes must provide `difftype` class argument"
            )
        Differ._differs[difftype] = cls

    def get_diff(self):
        return [d for d in self.get_possible_differences() if d.is_different()]

    @_abc.abstractmethod
    def get_possible_differences(self):
        pass

    def get_children(self):
        return []


class TypeDiffer(Differ, difftype=type):
    def get_possible_differences(self):
        typeid_diff = _differences.TypeIdentityDifference(self)
        type_diff = _differences.TypeDifference(self)
        # If the type is problematically different, it's obviously also not identical, but
        # we don't report both differences.
        return [type_diff] if type_diff.is_different() else [typeid_diff]


class SectionDiffer(Differ, difftype=_nrn.Section):
    def get_possible_differences(self):
        return [
            _differences.SectionLengthDifference(self),
            _differences.SectionDiamDifference(self),
            _differences.SectionAxialResistanceDifference(self),
            _differences.SectionMembraneCapacitanceDifference(self),
            _differences.SectionMembranePotentialDifference(self),
            _differences.SectionDiscretizationDifference(self),
            _differences.SectionPointDifference(self),
            _differences.SectionChildrenDifference(self),
        ]

    def get_children(self):
        # Use the difference class because it sorts the values
        child_sections = _differences.SectionChildrenDifference(self).get_values()
        return [
            # Child segments
            *zip(self.left, self.right),
            # Child sections
            *zip(*child_sections),
        ]


class SegmentDiffer(Differ, difftype=_nrn.Segment):
    def get_possible_differences(self):
        return [
            _differences.SegmentXDifference(self),
            _differences.SegmentAreaDifference(self),
            _differences.SegmentVolumeDifference(self),
            _differences.SegmentInputResistanceDifference(self),
            _differences.SegmentPotentialDifference(self),
            _differences.SegmentMechanismDifference(self),
        ]

    def get_children(self):
        # Use the difference class because it sorts the values
        child_mechs = _differences.SegmentMechanismDifference(self).get_values()
        return [
            # Child mechanisms
            *zip(*child_mechs),
            # Parent section
            (self.left.sec, self.right.sec),
        ]


class MechanismDiffer(Differ, difftype=_nrn.Mechanism):
    def get_possible_differences(self):
        return [_differences.SourceDifference(self)]

    def get_children(self):
        c = [
            # Parent segment
            (self.left.segment(), self.right.segment()),
            # Child parameters
            *zip(self.left, self.right),
        ]
        return [
            # Parent segment
            (self.left.segment(), self.right.segment()),
            # Child parameters
            *zip(self.left, self.right),
        ]


class ParameterDiffer(Differ, difftype=_nrn.RangeVar):
    def get_possible_differences(self):
        return [_differences.ParameterDifference(self)]

    def get_children(self):
        return [
            # Parent mech
            (self.left.mech(), self.right.mech())
        ]
