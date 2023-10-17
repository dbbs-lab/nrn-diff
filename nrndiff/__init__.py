"""
NEURON object differ. Recursively finds differences between objects in NEURON.
"""

from weakref import WeakSet
from collections import deque
from ._differs import TypeDiffer as _TypeDiffer, get_differ_for

__version__ = "0.0.1"
__all__ = ["nrn_diff", "get_differ_for"]


def nrn_diff(left, right):
    diff_bag = []
    memo = WeakSet()
    # The stack starts with a node of the given arguments and no parent differ.
    stack = deque([(left, right, None)])
    while True:
        try:
            # Get the next item in the stack to process
            left, right, parent = stack.pop()
        except IndexError:
            break
        # Check if there is a difference between the types.
        type_diffs = _TypeDiffer(left, right, parent).get_diff()
        diff_bag.extend(type_diffs)
        # If there is no type nrn_diff, or it's not a drastic type nrn_diff, check for normal nrn_diff
        if not type_diffs or all(diff.continue_diff() for diff in type_diffs):
            # See if there is a differ defined for this type, if not, skip this node
            differ_type = get_differ_for(left)
            if not differ_type:
                continue
            differ = differ_type(left, right, parent)
            # Get and store the list of differences between the objects
            diffs = differ.get_diff()
            diff_bag.extend(diffs)
            # No diffs that terminate diffing?
            if all(diff.continue_diff() for diff in diffs):
                # Then extend the stack with all the NEURON objects related to this pair
                # that we haven't visited yet.
                stack.extend(
                    (left_child, right_child, differ)
                    for (left_child, right_child) in differ.get_children(memo)[::-1]
                )
    return diff_bag


# NEURON patches


def _nrnmech_hash(self):
    return hash(f"seg:{hash(self.segment())}:mech:{self.name()}")


def _nrnmech_eq(self, other):
    return hash(self) == hash(other)


from neuron import nrn

nrn.Mechanism.__hash__ = _nrnmech_hash
nrn.Mechanism.__eq__ = _nrnmech_eq
