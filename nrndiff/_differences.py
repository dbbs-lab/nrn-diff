import abc as _abc
import numpy as _np
from neuron import h as _h


class Difference(_abc.ABC):
    def __init__(self, differ):
        self._differ = differ

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def differ(self):
        return self._differ

    @property
    def left(self):
        return self._differ.left

    @property
    def right(self):
        return self._differ.right

    def get_labels(self):
        return str(self.left), str(self.right)

    def continue_diff(self):
        return not self.is_different()

    @_abc.abstractmethod
    def get_values(self):
        pass

    def is_different(self):
        a, b = self.get_values()
        return a != b


class TypeDifference(Difference):
    def get_values(self):
        return type(self.differ.left), type(self.differ.right)

    def is_different(self):
        type_left, type_right = self.get_values()
        return not (
            isinstance(self.differ.left, type_right)
            or isinstance(self.differ.right, type_left)
        )


class TypeIdentityDifference(TypeDifference):
    def is_different(self):
        type_left, type_right = self.get_values()
        return type_left is not type_right

    def continue_diff(self):
        return True


class AttributeDifference(Difference):
    def __init_subclass__(cls, attr=None, **kwargs):
        if attr is None:
            raise TypeError("`attr` class argument missing.")
        cls._attr = attr

    def continue_diff(self):
        return True

    def get_values(self):
        l = getattr(self._differ.left, self._attr)
        r = getattr(self._differ.right, self._attr)
        return (l(), r()) if callable(l) else (l, r)


class SectionLengthDifference(AttributeDifference, attr="L"):
    pass


class SectionDiamDifference(AttributeDifference, attr="diam"):
    pass


class SectionAxialResistanceDifference(AttributeDifference, attr="Ra"):
    pass


class SectionMembraneCapacitanceDifference(AttributeDifference, attr="cm"):
    pass


class SectionMembranePotentialDifference(AttributeDifference, attr="v"):
    pass


class SectionDiscretizationDifference(AttributeDifference, attr="nseg"):
    def continue_diff(self):
        return not self.is_different()


class SegmentXDifference(AttributeDifference, attr="x"):
    pass


class SegmentAreaDifference(AttributeDifference, attr="area"):
    pass


class SegmentVolumeDifference(AttributeDifference, attr="volume"):
    pass


class SegmentInputResistanceDifference(AttributeDifference, attr="ri"):
    pass


class SegmentPotentialDifference(AttributeDifference, attr="v"):
    pass


class SectionPointDifference(Difference):
    def get_values(self):
        l, r = self.differ.left, self.differ.right
        return (
            _np.array(
                [(l.x3d(i), l.y3d(i), l.z3d(i), l.diam3d(i)) for i in range(l.n3d())]
            ),
            _np.array(
                [(r.x3d(i), r.y3d(i), r.z3d(i), r.diam3d(i)) for i in range(r.n3d())]
            ),
        )

    def is_different(self):
        l, r = self.get_values()
        return l.shape != r.shape or not _np.allclose(l, r)


class SectionChildrenDifference(Difference):
    def get_values(self):
        # todo: Maybe try to puzzle together a way to stable sort sections to improve
        #  diff robustness vs insert order.
        return self.differ.left.children(), self.differ.right.children()

    def is_different(self):
        left_children, right_children = self.get_values()
        return len(left_children) != len(right_children)


class SegmentMechanismDifference(Difference):
    def get_values(self):
        return [*self.differ.left], [*self.differ.right]

    def is_different(self):
        left, right = self.get_values()
        left_set = sorted(mech.name() for mech in left)
        right_set = sorted(mech.name() for mech in right)
        return left_set != right_set


class SourceDifference(Difference):
    def get_values(self):
        left_source = getattr(_h, self.differ.left.name()).file
        right_source = getattr(_h, self.differ.right.name()).file
        return left_source, right_source


class ParameterDifference(Difference):
    def get_labels(self):
        return (
            f"{self.left.mech().segment().name()}.{self.left.name()}",
            f"{self.right.mech().segment().name()}.{self.right.name()}",
        )

    def continue_diff(self):
        return True

    def get_values(self):
        # Compare parameter value, even though it might be missing on the right side:
        # differences in mechanism will be detected at some point anyway covering the
        # false positives in this logic.
        pname = self.differ.left.name()[: -len(self.differ.left.mech().name()) - 1]
        l = getattr(self._differ.left.mech(), pname, None)
        r = getattr(self._differ.right.mech(), pname, None)
        return l, r
