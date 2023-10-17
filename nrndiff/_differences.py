import abc


class Difference:
    def __init__(self, differ):
        self._differ = differ

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def differ(self):
        return self._differ

    def continue_diff(self):
        return not self.is_different()

    @abc.abstractmethod
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


class SectionChildrenDifference(Difference):
    def get_values(self):
        # todo: Maybe try to puzzle together a way to stable sort sections to improve
        #  diff robustness vs insert order.
        return self.differ.left.children(), self.differ.right.children()

    def is_different(self):
        left_children, right_children = self.get_values()
        return len(left_children) != len(right_children)
