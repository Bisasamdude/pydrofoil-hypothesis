import pytest
import _pydrofoil
from pydrofoilhypothesis import pydrofoilhypothesis
m = _pydrofoil.RISCV64()

def test_smoke_test_bitvector():
    # bitvector width 1
    typ = m.lowlevel.bit_str.sail_type.arguments[0]
    strategy = pydrofoilhypothesis.hypothesis_from_pydrofoil_type(typ)
    val = strategy.example()
    assert isinstance(val, _pydrofoil.bitvector)
    assert val == 1 or val == 0
    assert len(val) == 1
