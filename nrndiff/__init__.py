"""
NEURON object differ. Recursively finds differences between objects in NEURON.
"""
import gc
from typing import List, TYPE_CHECKING
from collections import deque
from . import _patches
from ._differs import TypeDiffer as _TypeDiffer, get_differ_for
from ._util import Memo

__version__ = "0.0.3"
__all__ = ["nrn_diff", "get_differ_for"]


if TYPE_CHECKING:
    from ._differences import Difference


def nrn_diff(left, right) -> List["Difference"]:
    diff_bag = []
    memo = Memo({left, right})
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
                # that we haven't visited yet, and add them to the memo.
                stack.extend(
                    (left_child, right_child, differ)
                    for (left_child, right_child) in memo.visit(differ.get_children())
                )
    del memo
    gc.collect()
    return diff_bag
