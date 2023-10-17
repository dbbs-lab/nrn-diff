"""This module patches a couple of __hash__ and __eq__ checks for stable comparisons"""
import gc as _gc
from neuron import nrn as _nrn, h as _h


def _nrnmech_hash(self):
    return hash(f"seg:{hash(self.segment())}:mech:{self.name()}")


def _nrnrangevar_hash(self):
    return hash(f"seg:{hash(self.mech().segment())}:param:{self.name()}")


def _hash_eq(self, other):
    return hash(self) == hash(other)


_s = _h.Section()
_s.insert("pas")
_RangeVar = type(next(iter(_s(0.5).pas)))

_nrn.Mechanism.__hash__ = _nrnmech_hash
_RangeVar.__hash__ = _nrnrangevar_hash
_nrn.Mechanism.__eq__ = _hash_eq
_RangeVar.__eq__ = _hash_eq

del _s
_nrn.RangeVar = _RangeVar
_gc.collect()
