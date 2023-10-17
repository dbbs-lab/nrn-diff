import abc
from . import _differences
from neuron import nrn


def get_differ_for(t):
    return Differ._differs.get(t, None)


class Differ(abc.ABC):
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

    @abc.abstractmethod
    def get_possible_differences(self):
        pass

    def get_children(self, memo):
        return []


class TypeDiffer(Differ, difftype=type):
    def get_possible_differences(self):
        typeid_diff = _differences.TypeIdentityDifference(self)
        type_diff = _differences.TypeDifference(self)
        # If the type is problematically different, it's obviously also not identical, but
        # we don't report both differences.
        return [type_diff] if type_diff.is_different() else [typeid_diff]


class SectionDiffer(Differ, difftype=nrn.Section):
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

    def get_children(self, memo):
        return [
            *zip(self.left, self.right),
            *zip(*_differences.SectionChildrenDifference(self).get_values()),
        ]


class SegmentDiffer(Differ, difftype=nrn.Segment):
    def get_possible_differences(self):
        return [
            _differences.SegmentXDifference(self),
            _differences.SegmentAreaDifference(self),
            _differences.SegmentVolumeDifference(self),
            _differences.SegmentInputResistanceDifference(self),
            _differences.SegmentPotentialDifference(self),
        ]

    def get_children(self, memo):
        return [*zip(self.left, self.right)]
