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

    def get_children(self, memo):
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

    def get_children(self, memo):
        child_sections = _differences.SectionChildrenDifference(self).get_values()
        return [
            # Child segments
            *_zip_memo(memo, self.left, self.right),
            # Child sections
            *_zip_memo(memo, *child_sections),
        ]


class SegmentDiffer(Differ, difftype=_nrn.Segment):
    def get_possible_differences(self):
        return [
            _differences.SegmentXDifference(self),
            _differences.SegmentAreaDifference(self),
            _differences.SegmentVolumeDifference(self),
            _differences.SegmentInputResistanceDifference(self),
            _differences.SegmentPotentialDifference(self),
        ]

    def get_children(self, memo):
        return [
            # Parent section
            *_single_memo(memo, self.left.sec, self.right.sec),
            # Child mechanisms
            *_zip_memo(memo, self.left, self.right),
        ]


def _zip_memo(memo: set, left, right):
    left = [l for l in left if l not in memo]
    right = [r for r in right if r not in memo]
    memo.update(left)
    memo.update(right)
    return zip(left, right)


def _single_memo(memo: set, left, right):
    if left in memo or right in memo:
        return []
    memo.add(left)
    memo.add(right)
    return [(left, right)]
